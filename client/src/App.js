import logo from "./logo.svg";
import "./App.css";
import { useEffect, useState } from "react";
import axios from "axios";
import { getPlayers, getRecentGames } from "./axios/posts";

function App() {
  const [players, setPlayers] = useState();
  const [games, setGames] = useState();
  
  
  useEffect(() => {
    const getPlayersReq = async () => {
      const playersReq = await getPlayers();
      setPlayers(playersReq);
    };
    const getGames = async () => {
      const games = await getRecentGames();
      setGames(games.games)
    };
    getPlayersReq();
    getGames();
  }, []);
  return (
    <div className="App">
      {games &&
        games.map((game) => {
          return (
            <div style={{ display: "flex", justifyContent: "center" }}>
              <div>{JSON.stringify(game)}</div>
            </div>
          );
        })}
        {JSON.stringify(players)}
    </div>
  );
}

export default App;
