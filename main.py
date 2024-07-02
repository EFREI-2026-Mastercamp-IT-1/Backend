from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
from starlette.middleware.cors import CORSMiddleware
from src.kruskal import Graph
from src.dijkstra import GraphDijkstra

app = FastAPI()

class Stop(BaseModel):
    stop_id: str
    stop_sequence: int
    lon: float
    lat: float
    stop_name: str

class DijkstraResponse(BaseModel):
    distance: float
    path: List[int]

def get_db_connection():
    conn = sqlite3.connect('src/mon_database.db')
    conn.row_factory = sqlite3.Row
    return conn

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://0.0.0.0:3147/",
        "https://frontend-v2-digj.onrender.com/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stops/{line_name}", response_model=List[Stop])
def read_stops(line_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {line_name} ORDER BY stop_sequence")
    stops = cursor.fetchall()
    return [Stop(**dict(stop)) for stop in stops]

@app.get("/stop/{line_name}/{stop_id}", response_model=Stop)
def read_stop(line_name: str, stop_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {line_name} WHERE stop_id = ?", (stop_id,))
    stop = cursor.fetchone()
    if stop is None:
        raise HTTPException(status_code=404, detail="Stop not found")
    return Stop(**dict(stop))


@app.get("/acpm")
def get_kruskal():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stations")
    nb_vertices = cursor.fetchall()
    nb_vertices = len(nb_vertices)
    g = Graph(nb_vertices)

    cursor.execute("SELECT * FROM concatligne")
    liaisons = [list(row) for row in cursor.fetchall()]

    for u, v, w in liaisons:
        g.add_edge(int(u), int(v), int(w))

    acpm = g.kruskal()

    cursor.execute("SELECT stop_ids,id FROM stations")
    stop_ids = cursor.fetchall()
    stop_ids = {id: stop_id.split(',')[0] for stop_id, id in stop_ids}

    acpm_id = [(stop_ids[u], stop_ids[v]) for u, v in acpm]

    return acpm_id


@app.get("/acpm/points")
def get_kruskal_points():
    kruskal = get_kruskal()

    points = []

    for u, v in kruskal:
        if u not in points:
            points.append(u)
        if v not in points:
            points.append(v)


    lines = ["ligne1","ligne2","ligne3","ligne3b", "ligne4", "ligne5", "ligne6", "ligne7", "ligne7b", "ligne8", "ligne9", "ligne10", "ligne11", "ligne12", "ligne13", "ligne14"]

    conn = get_db_connection()
    cursor = conn.cursor()

    stops = []

    for line in lines:
        cursor.execute(f"SELECT * FROM {line}")
        stops += cursor.fetchall()

    stops = [Stop(**dict(stop)) for stop in stops]

    points = [stop for stop in stops if stop.stop_id in points]

    return points

@app.get("/dijkstra/{src}/{dest}", response_model=DijkstraResponse)
def get_dijkstra(src: int, dest: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM stations")
    nb_vertices = cursor.fetchone()[0]

    g = GraphDijkstra(nb_vertices)

    cursor.execute("SELECT * FROM concatligne")
    liaisons = [list(row) for row in cursor.fetchall()]

    for u, v, w in liaisons:
        g.graph[int(u)][int(v)] = int(w)
        g.graph[int(v)][int(u)] = int(w)  # Assuming undirected graph

    if src >= nb_vertices or src < 0 or dest >= nb_vertices or dest < 0:
        raise HTTPException(status_code=400, detail="Invalid source or destination vertex")

    distance, path = g.shortest_path(src, dest)

    return DijkstraResponse(distance=distance, path=path)


@app.get("/stations/")
def read_stations():
    lines = ["ligne1","ligne2","ligne3","ligne3b", "ligne4", "ligne5", "ligne6", "ligne7", "ligne7b", "ligne8", "ligne9", "ligne10", "ligne11", "ligne12", "ligne13", "ligne14"]
    conn = get_db_connection()
    cursor = conn.cursor()
    stations = []
    for line in lines:
        cursor.execute(f"""
            SELECT nt.*, l.lon, l.lat, l.stop_sequence, l.stop_id as line_stop_id
            FROM stations nt
            JOIN {line} l ON nt.stop_ids LIKE '%' || l.stop_id || '%'
            ORDER BY l.stop_sequence
        """)
        line_stations = cursor.fetchall()
        for i, station in enumerate(line_stations):
            station_dict = dict(station)
            station_dict["line"] = line
            # Add the stop_id of the next station
            if i < len(line_stations) - 1:
                next_station_id = line_stations[i + 1]["line_stop_id"]
                cursor.execute(f"""
                    SELECT id
                    FROM stations
                    WHERE stop_ids LIKE '%' || ? || '%'
                """, (next_station_id,))
                next_station_new_table_id = cursor.fetchone()
                station_dict["next_stop_id"] = next_station_new_table_id["id"] if next_station_new_table_id else ""
            else:
                station_dict["next_stop_id"] = ""
            # Add the stop_id of the previous station
            if i > 0:
                prev_station_id = line_stations[i - 1]["line_stop_id"]
                cursor.execute(f"""
                    SELECT id
                    FROM stations
                    WHERE stop_ids LIKE '%' || ? || '%'
                """, (prev_station_id,))
                prev_station_new_table_id = cursor.fetchone()
                station_dict["prev_stop_id"] = prev_station_new_table_id["id"] if prev_station_new_table_id else ""
            else:
                station_dict["prev_stop_id"] = ""
            stations.append(station_dict)
    return stations
