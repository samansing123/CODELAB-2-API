import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

class MovieAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.img_base = "https://image.tmdb.org/t/p/w200"
       
        self.genre_list = {
            "Action": 28, "Comedy": 35, "Horror": 27, 
            "Drama": 18, "Sci-Fi": 878, "Romance": 10749
        }

    def get_trending(self):
        """Fetches pre-existing popular movies for the home screen."""
        url = f"{self.base_url}/movie/popular?api_key={self.api_key}"
        return requests.get(url).json().get('results', [])[:12]

    def get_by_genre(self, genre_name):
        """Queries the API based on the category ID."""
        genre_id = self.genre_list.get(genre_name)
        url = f"{self.base_url}/discover/movie?api_key={self.api_key}&with_genres={genre_id}"
        return requests.get(url).json().get('results', [])[:12]

    def search_movies(self, query):
        url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}"
        return requests.get(url).json().get('results', [])[:12]

class MovieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api = MovieAPI("60991b3138c3f10791cfb1d8e0cd2da3")
        self.title("Cinema Discovery Tool")
        self.geometry("1000x800")
        self.image_cache = [] 

        self._build_interface()
        self.display_movies(self.api.get_trending()) 

    def _build_interface(self):
        
        controls = tk.Frame(self, pady=20)
        controls.pack(fill="x")

        
        tk.Label(controls, text="Category:").pack(side="left", padx=5)
        self.genre_combo = ttk.Combobox(controls, values=list(self.api.genre_list.keys()))
        self.genre_combo.pack(side="left", padx=5)
        self.genre_combo.bind("<<ComboboxSelected>>", lambda e: self.display_movies(self.api.get_by_genre(self.genre_combo.get())))

        
        tk.Label(controls, text="  OR Search:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(controls, width=25)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(controls, text="Go", command=lambda: self.display_movies(self.api.search_movies(self.search_entry.get()))).pack(side="left")

        
        self.canvas = tk.Canvas(self)
        self.scroll_frame = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def display_movies(self, movies):
        """Clears and updates the screen with movie cards."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_cache = []

        if not movies:
            tk.Label(self.scroll_frame, text="No movies found.").pack()
            return

        for movie in movies:
            card = tk.Frame(self.scroll_frame, relief="ridge", borderwidth=2, pady=10)
            card.pack(fill="x", padx=20, pady=10)

            
            path = movie.get('poster_path')
            if path:
                try:
                    resp = requests.get(f"{self.api.img_base}{path}")
                    img = Image.open(BytesIO(resp.content)).resize((120, 180))
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache.append(photo)
                    tk.Label(card, image=photo).pack(side="left", padx=10)
                except: pass

            
            info = tk.Frame(card)
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=movie['title'], font=("Arial", 14, "bold")).pack(anchor="w")
            tk.Label(info, text=f"Release: {movie.get('release_date', 'N/A')}", fg="gray").pack(anchor="w")
            tk.Label(info, text=movie['overview'], wraplength=600, justify="left").pack(anchor="w", pady=5)

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()