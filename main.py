import flet as ft
import pandas as pd
import random

df = pd.read_csv('movies.csv', low_memory=False)

df['genres'] = df['genres'].fillna('')

def process_genres(genre_column):
    return [genre.strip() for genre in genre_column.replace('-', ',').split(',') if genre.strip()]

df['genre_names'] = df['genres'].apply(process_genres)

all_genres = set([genre for sublist in df['genre_names'] for genre in sublist])

genre_columns = {genre: [] for genre in all_genres}
for genres in df['genre_names']:
    for genre in all_genres:
        genre_columns[genre].append(1 if genre in genres else 0)

for genre, values in genre_columns.items():
    df[genre] = values

genre_columns_list = list(genre_columns.keys())
X = df[genre_columns_list]

# Function to get recommendations based on selected genres and language
def get_recommendations(primary_genre, secondary_genre, tertiary_genre, language):
    
    if not primary_genre or not secondary_genre or not tertiary_genre:
        return "Blank Space\n"  # Return if any genre is blank

    selected_genres = list(set([primary_genre, secondary_genre, tertiary_genre]))

    # Step 1: Filter movies by primary genre
    primary_matches = df[df[primary_genre] == 1]

    # Step 2: Filter movies by secondary genre within the primary matches
    secondary_matches = primary_matches[primary_matches[secondary_genre] == 1]

    # Step 3: Filter movies by tertiary genre within the secondary matches
    tertiary_matches = secondary_matches[secondary_matches[tertiary_genre] == 1]

    # Step 4: Filter by language
    if language:
        tertiary_matches = tertiary_matches[tertiary_matches['original_language'] == language]

    if tertiary_matches.shape[0] == 0:  # Check if there are no rows in the DataFrame
        return "No matching movies found for the selected genres and language.\n"

    if tertiary_matches.shape[0] > 0:
        # Randomly select a movie index from the filtered DataFrame
        random_index = random.choice(tertiary_matches.index.tolist())
        return tertiary_matches.loc[random_index].to_dict()  # Return the movie as a dictionary

    return "No matching movies found for the selected genres and language.\n"


# Step 1: Genre selection page
def main(page: ft.Page):
    page.title = "Wanna taste somethin', huh?"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    title_text = ft.Text(
        "Get Recommended a Movie", size=30, color="white", weight=ft.FontWeight.BOLD
    )

    page.bgcolor = "#121212"  # Dark background, like Material Design dark mode
    page.padding = 20  # Add padding for overall layout

    primary_genre_input = ft.Dropdown(
        label="Select Primary Genre",
        options=[ft.dropdown.Option(genre) for genre in all_genres],
        width=300,
        border_color="white",  # Material look, light border
        focused_border_color="blue",  # Focused state with a green border
    )

    secondary_genre_input = ft.Dropdown(
        label="Select Secondary Genre",
        options=[ft.dropdown.Option(genre) for genre in all_genres],
        width=300,
        border_color="white",
        focused_border_color="yellow",
    )

    tertiary_genre_input = ft.Dropdown(
        label="Select Tertiary Genre",
        options=[ft.dropdown.Option(genre) for genre in all_genres],
        width=300,
        border_color="white",
        focused_border_color="orange",
    )

    language_input = ft.Dropdown(
        label="Select Language",
        options=[ft.dropdown.Option(language) for language in df['original_language'].unique()],
        width=300,
        border_color="white",
        focused_border_color="green",
    )

    result_text = ft.Text(value="", size=18, color="white", text_align="center", font_family="Arial")  

    initial_genres = {
        "primary": None,
        "secondary": None,
        "tertiary": None,
        "language": None
    }

    recommend_button = ft.ElevatedButton(
        text="Get Recommendation",
        on_click=lambda e: handle_recommendation(
            page, primary_genre_input, secondary_genre_input, tertiary_genre_input, language_input, result_text, initial_genres
        ),
        color="green",  # Button color (green)
        width=200,  # Button width
    )

    credit_button = ft.Text(
        "Made by AJ", size=16, color="red", weight=ft.FontWeight.BOLD, font_family="Helvetica"
    )

    github_button = ft.ElevatedButton(
        text="GitHub",
        on_click=lambda e: page.launch_url("https://github.com/ajay-karmakar"),
        color="blue",  # Button color
        width=150,  # Button width
    )

    page.add(
        ft.ListView(
            expand=True,
            controls=[
                ft.Row(
                    [
                        ft.Column(
                            [
                                title_text, 
                                primary_genre_input,
                                secondary_genre_input,
                                tertiary_genre_input,
                                language_input,
                                recommend_button,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Container(
                                    content=result_text,
                                    width=350 if page.width < 600 else 500,  # Use 350px width on mobile, 500px on desktop
                                    padding=ft.Padding(10,10,10,10),  # top, right, bottom, left        
                                    alignment=ft.alignment.center,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [
                                credit_button,
                                github_button
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ]
        )
    )

# Handle recommendation logic
def handle_recommendation(page, primary_genre_input, secondary_genre_input, tertiary_genre_input, language_input, result_text, initial_genres):
    # Update the initial genres state with the current values
    primary_genre = primary_genre_input.value or initial_genres["primary"]
    secondary_genre = secondary_genre_input.value or initial_genres["secondary"]
    tertiary_genre = tertiary_genre_input.value or initial_genres["tertiary"]
    language = language_input.value or initial_genres["language"]

    # Save the current genre and language selection to retain it for future updates
    initial_genres["primary"] = primary_genre
    initial_genres["secondary"] = secondary_genre
    initial_genres["tertiary"] = tertiary_genre
    initial_genres["language"] = language

    # Get the recommendation or error message
    recommendation = get_recommendations(primary_genre, secondary_genre, tertiary_genre, language)

    # Check if recommendation is valid and not empty
    if isinstance(recommendation, str):  # If recommendation is a string, display the message
        result_text.value = recommendation
    elif recommendation is not None:  # If recommendation is not None and is a dictionary
        # Ensure 'title' and 'overview' are strings
        title = str(recommendation.get('title', 'No Title Available'))
        overview = str(recommendation.get('overview', 'No Overview Available'))
        release_date = str(recommendation.get('release_date', 'No Release Date'))
        language = str(recommendation.get('original_language', 'No Language Available'))
        popularity = str(recommendation.get('popularity', 'No Data Available'))

        result_text.value = f"{title}\n\nOverview: {overview[:200]}...\nRelease Date: {release_date}\nLanguage: {language}\nPopularity: {popularity}\n"

    else:
        result_text.value = "No matching movie found for the selected genres and language.\n"
    page.update()

ft.app(target=main)