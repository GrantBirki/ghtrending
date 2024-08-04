const DEFAULT_PATH = "trends/stars";
const SUFFIX = ".json";
const BASE_URL = "https://ghtrendingdata.birki.io";

async function fetchStars(path) {
  const response = await fetch(`${BASE_URL}/${DEFAULT_PATH}/${path}${SUFFIX}`, {
    headers: {
      Accept: "application/json",
    },
  });

  return await response.json();
}

export default fetchStars;
