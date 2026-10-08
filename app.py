import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from spotify_client import SpotifyClient
from comparator import compare_playlists
from exporter import export_excel, export_csv_bundle

class SpotifyCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Analyzer")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.client = None
        self.playlists = []
        self.results = None

        self.build_ui()
        self.authenticate()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Spotify Playlist Analyzer",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        ttk.Label(
            container,
            text="Compare playlists, inspect overlap, artists, duplicates, and export the results.",
        ).pack(anchor="w", pady=(4, 20))

        selection = ttk.LabelFrame(container, text="Playlist Selection", padding=15)
        selection.pack(fill="x")

        ttk.Label(selection, text="Playlist A").grid(row=0, column=0, sticky="w")
        ttk.Label(selection, text="Playlist B").grid(row=1, column=0, sticky="w", pady=(10, 0))

        self.playlist_a = ttk.Combobox(selection, state="readonly", width=70)
        self.playlist_b = ttk.Combobox(selection, state="readonly", width=70)
        self.playlist_a.grid(row=0, column=1, padx=10, sticky="ew")
        self.playlist_b.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")

        self.compare_button = ttk.Button(
            selection, text="Compare Playlists", command=self.start_compare
        )
        self.compare_button.grid(row=0, column=2, rowspan=2, padx=(15, 0), sticky="ns")

        selection.columnconfigure(1, weight=1)

        stats = ttk.LabelFrame(container, text="Summary", padding=15)
        stats.pack(fill="x", pady=15)

        self.stat_vars = {
            "a": tk.StringVar(value="—"),
            "b": tk.StringVar(value="—"),
            "common": tk.StringVar(value="—"),
            "only_a": tk.StringVar(value="—"),
            "only_b": tk.StringVar(value="—"),
            "overlap": tk.StringVar(value="—"),
        }

        labels = [
            ("Playlist A", "a"),
            ("Playlist B", "b"),
            ("Common", "common"),
            ("Only A", "only_a"),
            ("Only B", "only_b"),
            ("Overlap", "overlap"),
        ]

        for i, (label, key) in enumerate(labels):
            box = ttk.Frame(stats)
            box.grid(row=0, column=i, padx=10, sticky="nsew")
            ttk.Label(box, text=label).pack()
            ttk.Label(
                box, textvariable=self.stat_vars[key], font=("Segoe UI", 18, "bold")
            ).pack(pady=(5, 0))
            stats.columnconfigure(i, weight=1)

        tabs = ttk.Notebook(container)
        tabs.pack(fill="both", expand=True)

        self.tabs = tabs
        self.tables = {}

        for key, title in [
            ("common", "Common Tracks"),
            ("only_a", "Only Playlist A"),
            ("only_b", "Only Playlist B"),
            ("artists", "Artists"),
            ("duplicates_a", "Duplicates A"),
            ("duplicates_b", "Duplicates B"),
        ]:
            frame = ttk.Frame(tabs, padding=8)
            tabs.add(frame, text=title)
            tree = ttk.Treeview(frame, show="headings")
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            self.tables[key] = tree

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=(12, 0))

        ttk.Button(buttons, text="Export Excel", command=self.save_excel).pack(side="left")
        ttk.Button(buttons, text="Export CSV Bundle", command=self.save_csv).pack(
            side="left", padx=8
        )

        self.status = tk.StringVar(value="Starting…")
        ttk.Label(buttons, textvariable=self.status).pack(side="right")

    def authenticate(self):
        def worker():
            try:
                self.client = SpotifyClient()
                self.root.after(0, self.load_playlists)
            except Exception as exc:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Spotify Authentication Error",
                        str(exc),
                    ),
                )
                self.root.after(0, lambda: self.status.set("Authentication failed"))

        threading.Thread(target=worker, daemon=True).start()

    def load_playlists(self):
        try:
            self.status.set("Loading playlists…")
            self.playlists = self.client.get_all_playlists()
            names = [f"{p['name']}  ({p['track_count']} tracks)" for p in self.playlists]
            self.playlist_a["values"] = names
            self.playlist_b["values"] = names
            if names:
                self.playlist_a.current(0)
                if len(names) > 1:
                    self.playlist_b.current(1)
            self.status.set(f"Loaded {len(names)} playlists")
        except Exception as exc:
            messagebox.showerror("Playlist Error", str(exc))
            self.status.set("Failed to load playlists")

    def start_compare(self):
        if not self.playlists:
            return
        a_index = self.playlist_a.current()
        b_index = self.playlist_b.current()
        if a_index < 0 or b_index < 0:
            messagebox.showwarning("Select Playlists", "Choose both playlists first.")
            return

        self.compare_button.config(state="disabled")
        self.status.set("Comparing…")

        def worker():
            try:
                a = self.playlists[a_index]
                b = self.playlists[b_index]
                tracks_a = self.client.get_playlist_tracks(a["id"])
                tracks_b = self.client.get_playlist_tracks(b["id"])
                results = compare_playlists(a, b, tracks_a, tracks_b)
                self.root.after(0, lambda: self.show_results(results))
            except Exception as exc:
                self.root.after(
                    0,
                    lambda: messagebox.showerror("Comparison Error", str(exc)),
                )
            finally:
                self.root.after(0, lambda: self.compare_button.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def show_results(self, results):
        self.results = results
        summary = results["summary"]

        self.stat_vars["a"].set(summary["playlist_a_tracks"])
        self.stat_vars["b"].set(summary["playlist_b_tracks"])
        self.stat_vars["common"].set(summary["common_tracks"])
        self.stat_vars["only_a"].set(summary["only_a"])
        self.stat_vars["only_b"].set(summary["only_b"])
        self.stat_vars["overlap"].set(f"{summary['overlap_percent']:.1f}%")

        self.fill_tree("common", results["common_tracks"])
        self.fill_tree("only_a", results["only_a_tracks"])
        self.fill_tree("only_b", results["only_b_tracks"])
        self.fill_tree("artists", results["artist_comparison"])
        self.fill_tree("duplicates_a", results["duplicates_a"])
        self.fill_tree("duplicates_b", results["duplicates_b"])

        self.status.set("Comparison complete")

    def fill_tree(self, key, rows):
        tree = self.tables[key]
        tree.delete(*tree.get_children())

        if not rows:
            tree["columns"] = ("message",)
            tree.heading("message", text="Result")
            tree.column("message", width=700)
            tree.insert("", "end", values=("No results",))
            return

        columns = list(rows[0].keys())
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=160, anchor="w")

        for row in rows:
            tree.insert("", "end", values=[row.get(col, "") for col in columns])

    def save_excel(self):
        if not self.results:
            messagebox.showwarning("No Results", "Run a comparison first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if path:
            export_excel(self.results, path)
            self.status.set(f"Exported: {path}")

    def save_csv(self):
        if not self.results:
            messagebox.showwarning("No Results", "Run a comparison first.")
            return
        folder = filedialog.askdirectory()
        if folder:
            export_csv_bundle(self.results, folder)
            self.status.set(f"CSV files exported to {folder}")


if __name__ == "__main__":
    root = tk.Tk()
    SpotifyCompareApp(root)
    root.mainloop()
