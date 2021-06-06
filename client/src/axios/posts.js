import axios from "axios";

export const getRecentGames = async (page = 1) => {
  const gamesResponse = await axios.get(
    "/recent-games/CambridgeON/" + page
  );
  return gamesResponse.data;
};

export const getPlayers = async () => {
    const response = await axios.get("/get_players");
    return response.data
  };


