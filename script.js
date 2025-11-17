async function fetchData() {

    try{
        const pokemonName = document.getElementById("pokemonInput").value.toLowerCase();
        const response = await fetch(`https://pokeapi.co/api/v2/pokemon/${pokemonName}`);
    
        if (!response.ok) {
            throw new Error('Could not fetch data');
        }

        const data = await response.json();
        const pokemonSprite = data.sprites.front_default;
        const imgElement =document.getElementById("pokemonSprite");

        imgElement.src = pokemonSprite;
        imgElement.style.display = "block";
    } catch (error) {
        console.error(error);
        const imgElement = document.getElementById("pokemonSprite");
        if (imgElement) {
            imgElement.style.display = "none";
        }
        alert('Could not fetch that Pokémon. Check the name and try again.');
    }
}


const weatherForm = document.querySelector('.weatherForm');
const cityInput = document.querySelector('.cityInput');
const card = document.querySelector('.card');
const apiKey = "21ea21029dce44c9ddef8304b695213f";

weatherForm.addEventListener('submit', async event => {

    event.preventDefault();

    const city = cityInput.value;

    if (city) {
        try{
            const weatherData = await getWeatherData(city);
            displayWeatherInfo(weatherData);
        }
        catch(error){
            console.error(error);
            displayError('Failed to fetch weather data. Please try again later.');
        }
    }
    else{
        displayError('Please enter a city.');
    }
});

async function getWeatherData(city) {
    if (!city) throw new Error('City is required');

    const geoUrl = `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(city)}&limit=1&appid=${apiKey}`;
    const geoResp = await fetch(geoUrl);
    if (!geoResp.ok) throw new Error('Failed to lookup city coordinates');
    const geoJson = await geoResp.json();
    if (!Array.isArray(geoJson) || geoJson.length === 0) throw new Error('City not found');
    const { lat, lon, name, country } = geoJson[0];

    const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`;
    const weatherResp = await fetch(weatherUrl);
    if (!weatherResp.ok) throw new Error('Failed to fetch weather data');
    const weatherJson = await weatherResp.json();

    weatherJson.resolvedName = `${name}${country ? ', ' + country : ''}`;
    return weatherJson;
}

function displayWeatherInfo(data) {
    if (!card) return;
    card.textContent = '';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';

    const title = document.createElement('h3');
    title.textContent = data.resolvedName || data.name || 'Weather';

    const emoji = document.createElement('div');
    emoji.textContent = getWeatherEmoji(data.weather && data.weather[0] && data.weather[0].id);
    emoji.style.fontSize = '2rem';

    const temp = document.createElement('p');
    temp.textContent = `Temperature: ${Math.round(data.main.temp)}°C`;

    const desc = document.createElement('p');
    desc.textContent = `Conditions: ${data.weather && data.weather[0] ? data.weather[0].description : 'N/A'}`;

    const humidity = document.createElement('p');
    humidity.textContent = `Humidity: ${data.main.humidity}%`;

    const wind = document.createElement('p');
    wind.textContent = `Wind: ${data.wind.speed} m/s`;

    card.appendChild(title);
    card.appendChild(emoji);
    card.appendChild(temp);
    card.appendChild(desc);
    card.appendChild(humidity);
    card.appendChild(wind);
}

function getWeatherEmoji(weatherId) {
    if (!weatherId) return '❓';
    if (weatherId >= 200 && weatherId < 300) return '⛈️';
    if (weatherId >= 300 && weatherId < 400) return '🌦️';
    if (weatherId >= 500 && weatherId < 600) return '🌧️';
    if (weatherId >= 600 && weatherId < 700) return '❄️';
    if (weatherId >= 700 && weatherId < 800) return '🌫️';
    if (weatherId === 800) return '☀️';
    if (weatherId > 800 && weatherId < 900) return '☁️';
    return '🌡️';
}

function displayError(message) {

    const errorDisplay = document.createElement("p");
    errorDisplay.textContent = message;
    errorDisplay.classList.add("errorDisplay");

    card.textContent = '';
    card.style.display = "flex";
    card.appendChild(errorDisplay);
}