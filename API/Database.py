import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

class MovieAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.img_base = "https://image.tmdb.org/t/p/w400"
        self.genre_map = {28: "Action", 35: "Comedy", 27: "Horror", 18: "Drama", 878: "Sci-Fi", 10749: "Romance"}

    def get_trending(self):
        url = f"{self.base_url}/movie/popular?api_key={self.api_key}"
        return requests.get(url).json().get('results', [])[:15]

    def get_by_genre(self, genre_id):
        url = f"{self.base_url}/discover/movie?api_key={self.api_key}&with_genres={genre_id}"
        return requests.get(url).json().get('results', [])[:15]

    def search_movies(self, query):
        url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}"
        return requests.get(url).json().get('results', [])[:15]

    def get_extra_details(self, movie_id):
        credits_url = f"{self.base_url}/movie/{movie_id}/credits?api_key={self.api_key}"
        details_url = f"{self.base_url}/movie/{movie_id}?api_key={self.api_key}"
        credits = requests.get(credits_url).json()
        details = requests.get(details_url).json()
        return details, credits

class MovieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api = MovieAPI("60991b3138c3f10791cfb1d8e0cd2da3") 
        self.title("The Movie Database")
        self.geometry("1920x1080")
        self.image_cache = []

        self._build_interface()
        self.display_movies(self.api.get_trending())

    def _build_interface(self):
        nav = tk.Frame(self, bg="#ffffff", pady=10)
        nav.pack(fill="x")

        tk.Label(nav, text="Category:", bg="#ffffff", fg="black").pack(side="left", padx=10)
        genre_ids = {"Action": 28, "Comedy": 35, "Horror": 27, "Drama": 18, "Sci-Fi": 878}
        self.genre_combo = ttk.Combobox(nav, values=list(genre_ids.keys()), state="readonly")
        self.genre_combo.pack(side="left", padx=5)
        self.genre_combo.bind("<<ComboboxSelected>>", lambda e: self.display_movies(self.api.get_by_genre(genre_ids[self.genre_combo.get()])))

        self.search_entry = tk.Entry(nav, width=30)
        self.search_entry.pack(side="left", padx=20)
        tk.Button(nav, text="Search", command=self.perform_search).pack(side="left")

        self.canvas = tk.Canvas(self, bg="#f5f5f5")
        self.scroll_frame = tk.Frame(self.canvas, bg="#f5f5f5")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def perform_search(self):
        query = self.search_entry.get()
        if query:
            self.display_movies(self.api.search_movies(query))

    def display_movies(self, movies):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_cache = []

        for movie in movies:
            card = tk.Frame(self.scroll_frame, relief="ridge", bd=1, bg="white", pady=10)
            card.pack(fill="x", padx=40, pady=10)

           
            path = movie.get('poster_path')
            if path:
                try:
                    resp = requests.get(f"https://image.tmdb.org/t/p/w154{path}")
                    img = ImageTk.PhotoImage(Image.open(BytesIO(resp.content)))
                    self.image_cache.append(img)
                    tk.Label(card, image=img, bg="white").pack(side="left", padx=15)
                except: pass

            
            info_frame = tk.Frame(card, bg="white")
            info_frame.pack(side="left", fill="both", expand=True)
            
            
            tk.Label(info_frame, text=movie['title'], font=("Helvetica", 16, "bold"), bg="white").pack(anchor="w")
            tk.Label(info_frame, text=f"Release: {movie.get('release_date', 'N/A')}", bg="white", fg="gray").pack(anchor="w")
            
           
            genre_ids = movie.get('genre_ids', [])
            names = [self.api.genre_map.get(gid, "Movie") for gid in genre_ids[:2]] # Show top 2
            tk.Label(info_frame, text=f"Genre: {' / '.join(names)}", bg="white", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=2)
            
            
            tk.Label(info_frame, text=f"⭐ {movie.get('vote_average')}/10", bg="white", font=("Helvetica", 11, "bold"), fg="#e67e22").pack(anchor="w", pady=2)
            
            
            read_more_btn = tk.Button(info_frame, text="Read More", bg="#ffffff", fg="black", font=("Helvetica", 10, "bold"),
                                      command=lambda m=movie: self.show_expanded_details(m))
            read_more_btn.pack(side="bottom", anchor="w", pady=5)

    def show_expanded_details(self, movie_summary):
        """Fetches extra info and displays in a pop-up window."""
        details, credits = self.api.get_extra_details(movie_summary['id'])
        
        pop = tk.Toplevel(self)
        pop.title(f"Detailed View: {details['title']}")
        pop.geometry("600x850")
        pop.configure(padx=20, pady=20)

       
        path = details.get('poster_path')
        if path:
            img_data = requests.get(f"{self.api.img_base}{path}").content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize((250, 375)))
            lbl = tk.Label(pop, image=img)
            lbl.image = img
            lbl.pack()

       
        tk.Label(pop, text=details['title'], font=("Arial", 18, "bold")).pack(pady=5)
        
        genres = [g['name'] for g in details.get('genres', [])]
        tk.Label(pop, text=f"⭐ {details.get('vote_average')}/10  |  📁 {', '.join(genres)}", font=("Arial", 11, "bold")).pack()

        countries = [c['name'] for c in details.get('production_countries', [])]
        country_str = ", ".join(countries) if countries else "Unknown"
        tk.Label(pop, text=f"📍 Country: {country_str}  |  📅 Date: {details.get('release_date')}").pack(pady=5)

        cast_list = [member['name'] for member in credits.get('cast', [])[:8]]
        tk.Label(pop, text="Main Cast:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10,0))
        tk.Label(pop, text=", ".join(cast_list), wraplength=550, justify="left").pack(anchor="w")

        tk.Label(pop, text="About the movie:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10,0))
        desc = tk.Text(pop, wrap="word", height=8, bg="#f9f9f9", bd=0, font=("Arial", 10))
        desc.insert("1.0", details.get('overview', 'No summary available.'))
        desc.config(state="disabled")
        desc.pack(fill="both", expand=True, pady=10)

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()