# Movie Recommender System

This project is a Movie Recommender System built using Flask, SQLAlchemy, and The Movie Database (TMDb) API. The application allows users to register, log in, and receive movie recommendations based on a selected movie. The recommendations are generated using a content-based filtering approach.

# Dataset
The dataset used in this project can be obtained from https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata. Ensure to download the dataset and extract the required files to the project root directory.

## Features

- **User Registration and Login**: Users can create an account and log in securely.
- **Movie Recommendations**: Users can select a movie, and the system will recommend similar movies based on a similarity matrix.
- **Movie Details**: Fetches and displays movie details including title, description, and poster image using TMDb API.
- **Pagination**: Displays movie recommendations in a paginated format.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **Flask-SQLAlchemy**: An extension for Flask that adds support for SQLAlchemy.
- **Flask-Login**: An extension that manages user sessions.
- **SQLite**: A lightweight database used for storing user and movie data.
- **Pandas**: For data manipulation and analysis.
- **Requests**: For making API calls to the TMDb API.
- **HTML/CSS**: For the front-end design.

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/movie-recommender-system.git
    cd movie-recommender-system
    ```

2. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Download and prepare the movie data**:
   - Ensure you have the following files:
     - `movie_dict.pkl`: Contains movie data.
     - `similarity.pkl`: Contains the movie similarity matrix.
   - Place these files in the project root directory.

4. **Set up the database**:
   - The database will be automatically created upon running the application for the first time.

5. **Run the application**:
    ```bash
    python app.py
    ```
   - Open your browser and navigate to `http://127.0.0.1:5000/`.

## Usage

- **Register**: Click on the register link, fill out the form, and create your account.
- **Login**: Use your credentials to log in.
- **Get Recommendations**: Select a movie from the dropdown and click "Recommend" to see similar movies.

## API Key

To use the TMDb API, you need to replace `API_KEY` in the code with your TMDb API key. You can obtain it by creating an account on the [TMDb website](https://www.themoviedb.org/documentation/api).

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was assigned as part of the Codex Cue solution. Special thanks to Codex Cue for the opportunity to work on this task.

