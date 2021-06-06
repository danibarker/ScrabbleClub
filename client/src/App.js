import logo from './logo.svg';
import './App.css';
import {useEffect, useState} from 'react'
import axios from 'axios'

function App() {
  const [players, setPlayers] = useState()
  const convertPlayersData = (response) => {
    response = response.replace(/\(/g, "[");
    response = response.replace(/\)/g, "]");
    response = response.replace(/None/g, null);
    response = response.replace(/'/g, '"');
    const data = JSON.parse(response);
    const cols = [
      "id",
      "first_name",
      "last_name",
      "discord",
      "woogles",
      "abbrev",
      "rating",
      "rung",
      "full_name",
      "current_opponent",
    ];
    return data.map((person) => {
      return person.reduce((personOb, data, index) => {
        personOb[cols[index]] = data;
        return personOb;
      }, {});
    });
  };
  useEffect(()=>{
    const getPlayers = async ()=>{
      const response = await axios.get('/get_players')
      setPlayers(convertPlayersData(response.data))

    }
    getPlayers()
  },[])
  return (
    <div className="App">
      {players && players.map(player=>{
        return <div>{player.name}</div>
      })}
    </div>
  );
}

export default App;
