import time
import traceback
import subprocess
import threading
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

class PlayerStatsGUI:
    def __init__(self):
        self.last_url = None
        self.players_data = {}
        self.teams_data = {}
        self.checked_players = {}
        self.checkbutton_vars = {}
        self.betting_sheets = []
        self.toggle_switch_buttons = {}
        self.betting_sheet_window = None  # Store reference to the betting sheet window

        self.root = Tk()
        self.root.title('Apex Legends Tournament Stats')
        self.root.geometry("1170x600")
        self.root.config(bg="#2C2F33")

        title_label = Label(self.root, text="Apex Legends Tournament Stats", font=("Arial", 24, "bold"), bg="#2C2F33",
                            fg="#FFFFFF")
        title_label.pack(pady=20)

        url_frame = Frame(self.root, bg="#2C2F33")
        url_frame.pack(pady=10)

        self.url_entry = Entry(url_frame, width=60, font=("Arial", 12), bd=2)
        self.url_entry.pack(side=LEFT, padx=10)

        self.show_results_button = Button(url_frame, text="Scrape Data", font=("Arial", 12, "bold"), bg="#7289DA",
                                          fg="#FFFFFF", bd=0, padx=20, pady=5, command=self.get_teams_and_scores)
        self.show_results_button.pack(side=LEFT, padx=10)

        self.link_button = Button(url_frame, text="Copy Last URL", font=("Arial", 12), bg="#7289DA", fg="#FFFFFF",
                                  bd=0, padx=20, pady=5, command=self.copy_last_url)
        self.link_button.pack(side=RIGHT, padx=10)

        self.scrape_button = Button(url_frame, text="Scrape PrizePickers", font=("Arial", 12), bg="#7289DA", fg="#FFFFFF",
                                    bd=0, padx=20, pady=5, command=self.scrape_prize_pickers)
        self.scrape_button.pack(side=RIGHT, padx=10)

        search_frame = Frame(self.root, bg="#2C2F33")
        search_frame.pack(pady=10)

        self.search_entry = Entry(search_frame, width=60, font=("Arial", 12), bd=2)
        self.search_entry.pack(side=LEFT, padx=10)
        self.search_entry.bind("<KeyRelease>", self.dynamic_search)

        self.start_over_button = Button(search_frame, text="Start Over", font=("Arial", 12), bg="#7289DA",
                                        fg="#FFFFFF", bd=0, padx=20, pady=5, command=self.start_over)
        self.start_over_button.pack(side=LEFT, padx=10)

        self.add_to_betting_sheet_button = Button(search_frame, text="Add to Betting Sheet", font=("Arial", 12),bg="#7289DA", fg="#FFFFFF", bd=0, padx=20, pady=5,command=self.add_to_betting_sheet, state=DISABLED)
        self.add_to_betting_sheet_button.pack(side=RIGHT, padx=10)

        # Create the canvas and configure it for scrolling
        scrollable_frame = Frame(self.root, bg="#2C2F33")
        scrollable_frame.pack(fill="both", expand=True)

        # Inside __init__ method after creating the canvas
        self.canvas = Canvas(scrollable_frame, bg="#2C2F33", takefocus=True)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Bind mouse wheel event to canvas
        self.canvas.focus_set()  # Set focus to the canvas

        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.scrollable_content = Frame(self.canvas, bg="#2C2F33")
        self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")

        self.checkbuttons_frame = Frame(self.scrollable_content, bg="#2C2F33")  # Initialize checkbuttons_frame
        self.checkbuttons_frame.pack(side=RIGHT, fill="y", pady=20, padx=10)

        on_image = Image.open("on.png")
        off_image = Image.open("off.png")

        on_image = on_image.resize((60, 20), Image.LANCZOS)
        off_image = off_image.resize((60, 20), Image.LANCZOS)

        self.on_photo = ImageTk.PhotoImage(on_image)
        self.off_photo = ImageTk.PhotoImage(off_image)

        self.lock_in_button = Button(search_frame, text="Lock In (0)", font=("Arial", 12),
                                     command=self.lock_in_players)
        self.lock_in_button.pack(side=RIGHT, padx=10)

        self.root.bind("<MouseWheel>", self.on_mousewheel)

    def scrape_prize_pickers(self):
        # Execute scrapePP.py in a separate thread
        threading.Thread(target=self.execute_scrape_pp).start()

    def execute_scrape_pp(self):
        try:
            output = subprocess.check_output(['python', 'scrapePP.py'], stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print("Error executing scrapePP.py:", e.output)
            return

        # Parse the output to extract options
        options_output = []
        for line in output.split('\n'):
            if line.strip().startswith('Enter your selection (number):'):
                break
            options_output.append(line.strip())

        # Prompt the user for selection
        selected_option = simpledialog.askinteger("PrizePickers Selection", "Select an option:\n" + "\n".join(options_output))

        if selected_option:
            # Print the user's selection
            print("User selected option:", selected_option)

            # Run scrapePP.py with the selected option
            # This is where you would execute scrapePP.py with the selected option
            # For now, let's just print a message indicating what would be done
            print("Running scrapePP.py with selected option:", selected_option)


    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_teams_and_scores(self):
        url = self.url_entry.get()
        self.last_url = url
        for widget in self.checkbuttons_frame.winfo_children():
            widget.destroy()
        self.checked_players.clear()

        try:
            driver = webdriver.Chrome()
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            scores_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div/div[1]/div[1]/div/div[1]')))
            scores_button.click()

            team_names_elems = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'recapScoreTeamName-team')))
            player_names_elems = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'recapScoreTeamName-players')))

            for team_name_elem, player_names_elem in zip(team_names_elems, player_names_elems):
                team_name = team_name_elem.text.strip()
                player_names = [name.strip() for name in player_names_elem.text.split('/')]
                self.teams_data[team_name] = player_names

            self.get_scores(driver)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data from URL: {e}")
            print("Error:", e)
            traceback.print_exc()
        finally:
            driver.quit()

    def get_scores(self, driver):
        wait = WebDriverWait(driver, 10)
        player_stats_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[2]/div/div[1]/div[1]/div/div[4]')))
        player_stats_button.click()

        player_stats_section = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                               '/html/body/div/div[2]/div[2]/div/div[1]/div[5]/div/div/div/div/div/table/tbody')))

        time.sleep(3)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        table = soup.find('table', {'id': 'playersStatsTable'})
        if table is None:
            raise ValueError("Player stats table not found on the page")

        new_players_data = {}
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 9:
                player_name = cols[0].get_text(strip=True)
                kills = int(cols[2].get_text(strip=True))
                damage = int(cols[5].get_text(strip=True).replace(',', ''))
                knocks = int(cols[4].get_text(strip=True))
                revives = int(cols[8].get_text(strip=True))

                if player_name in self.players_data:
                    existing_data = self.players_data[player_name]
                    existing_data['Kills'] += kills
                    existing_data['Damage'] += damage
                    existing_data['Knocks'] += knocks
                    existing_data['Revives'] += revives
                else:
                    new_players_data[player_name] = {
                        'Kills': kills,
                        'Damage': damage,
                        'Knocks': knocks,
                        'Revives': revives
                    }

        self.players_data.update(new_players_data)

        for team, players in self.teams_data.items():
            for player in players:
                if player in self.players_data:
                    self.players_data[player]['Team'] = team

        self.display_results(self.players_data)

    def display_results(self, players_data):
        if players_data:
            for player, data in players_data.items():
                kills = data['Kills']
                damage = data['Damage']
                kd = kills / (data['Knocks'] + data['Revives']) if data['Knocks'] + data['Revives'] != 0 else 0
                team = data.get('Team', 'Unknown')

                player_frame = Frame(self.checkbuttons_frame, bg="#2C2F33")
                player_frame.pack(fill="x", padx=10, pady=5)

                player_info = f"Player: {player}\nTeam: {team}\nKills: {kills}\nDamage: {damage}\nKD: {kd:.2f}"
                label = Label(player_frame, text=player_info, font=("Arial", 12), bg="#2C2F33", fg="#FFFFFF",
                              anchor="w", justify="left")
                label.pack(side="left", fill="both", expand=True)

                # Create check button
                var = IntVar()
                self.checkbutton_vars[player] = var  # Store IntVar for checkbutton
                checkbutton = Checkbutton(player_frame, text=f"Add {player} to Betting Sheet", variable=var, onvalue=1,
                                          offvalue=0, bg="#2C2F33", fg="#FFFFFF", selectcolor="black",
                                          command=lambda v=var, p=player: self.update_checked_players(v, p))
                checkbutton.pack(side="right")

                # Create toggle switch
                switch_frame = Frame(player_frame, bg="#2C2F33")
                switch_frame.pack(side="right")

                toggle_switch = Button(switch_frame, image=self.on_photo, bd=0, bg="#2C2F33", activebackground="#2C2F33",
                                       command=lambda p=player: self.toggle_switch(p))
                toggle_switch.pack()

                toggle_switch.config(image=self.off_photo)
                self.toggle_switch_buttons[player] = toggle_switch  # Store the toggle switch button

        else:
            label = Label(self.checkbuttons_frame, text="No player stats found.", font=("Arial", 12), bg="#2C2F33",
                          fg="#FFFFFF")
            label.pack(fill="both", padx=10, pady=5)

        # Update the canvas to reflect the new content size
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def toggle_switch(self, player):
        current_image = self.toggle_switch_buttons[player].cget('image')
        if current_image == str(self.on_photo):
            self.checked_players[player] = self.checkbutton_vars[player].get() == 1
            self.toggle_switch_buttons[player].config(image=self.off_photo)
        else:
            self.checked_players[player] = False
            self.toggle_switch_buttons[player].config(image=self.on_photo)

    def copy_last_url(self):
        if self.last_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_url)
        else:
            messagebox.showinfo("No URL", "No URL to copy.")

    def start_over(self):
        self.url_entry.delete(0, END)
        self.search_entry.delete(0, END)
        self.last_url = None
        self.players_data = {}
        self.teams_data = {}
        self.checked_players.clear()
        for widget in self.checkbuttons_frame.winfo_children():
            widget.destroy()
        self.add_to_betting_sheet_button.config(text="Add to Betting Sheet", state=DISABLED)
        self.lock_in_button.config(text=f"Lock In (0)")

    def dynamic_search(self, event):
        query = self.search_entry.get().strip().lower()
        if query:
            filtered_data = {}
            for player, data in self.players_data.items():
                if query in player.lower():
                    filtered_data[player] = data
            for team, players in self.teams_data.items():
                if query in team.lower():
                    for player in players:
                        if player in self.players_data:
                            filtered_data[player] = self.players_data[player]

            for widget in self.checkbuttons_frame.winfo_children():
                widget.destroy()
            self.display_results(filtered_data)
        else:
            for widget in self.checkbuttons_frame.winfo_children():
                widget.destroy()
            self.display_results(self.players_data)

    def update_checked_players(self, var, player):
        if var.get() == 1:  # Checkbox is checked
            # Always add the player to the final array
            self.checked_players[player] = True
        else:
            # If checkbox is unchecked, remove the player from the final array
            self.checked_players.pop(player, None)

        self.update_betting_sheet_label()

    def update_betting_sheet_label(self):
        count = len(self.checked_players)
        if count == 6:
            self.add_to_betting_sheet_button.config(text="Add to Betting Sheet", state=NORMAL)
        else:
            self.add_to_betting_sheet_button.config(text=f"Add to Betting Sheet ({count}/6)", state=DISABLED)

        print("Betting sheet button text:", self.add_to_betting_sheet_button.cget('text'))  # Debug print

    def add_to_betting_sheet(self):
        selected_players = []
        for player, checked in self.checked_players.items():
            selected_players.append((player, not checked))  # Reverse the value to match the requirement (False for More, True for Less)

        print("Selected players:", selected_players)
        self.betting_sheets.append(selected_players)
        messagebox.showinfo("Success", "Players added to Betting Sheet successfully!")

        # Reset all checkboxes and toggles
        for player, var in self.checkbutton_vars.items():
            var.set(0)
            self.checked_players[player] = False
            self.toggle_switch_buttons[player].config(image=self.off_photo)

        # Clear the checked players dictionary
        self.checked_players.clear()

        # Update the "Lock In" button text
        lock_in_count = len(self.betting_sheets)
        self.lock_in_button.config(text=f"Lock In ({lock_in_count})")

        # Update the "Add to Betting Sheet" button text
        self.update_betting_sheet_label()

    def lock_in_players(self):
        lock_in_count = len(self.betting_sheets)
        self.lock_in_button.config(text=f"Lock In ({lock_in_count})")

        # Open the betting sheet only if there are players added
        if self.betting_sheets:
            # Ensure there are no previous instances of the betting sheet window
            self.close_betting_sheet_window()

            # Open the betting sheet
            self.open_betting_sheet()

    def close_betting_sheet_window(self):
        if self.betting_sheet_window:
            self.betting_sheet_window.destroy()

    def open_betting_sheet(self):
        self.close_betting_sheet_window()  # Close existing betting sheet window if open

        # Create a new window for the betting sheet
        self.betting_sheet_window = Toplevel(self.root)
        self.betting_sheet_window.title("Betting Sheet")
        self.betting_sheet_window.geometry("800x600")  # Set a larger size for the window

        # Create a frame to contain the betting sheet content
        betting_sheet_frame = Frame(self.betting_sheet_window, bg="#2C2F33")
        betting_sheet_frame.pack(fill="both", expand=True)

        # Create headers for "Line" and "More/Less" columns
        line_label = Label(betting_sheet_frame, text="Line", font=("Arial", 12, "bold"), bg="#2C2F33", fg="#FFFFFF")
        line_label.grid(row=0, column=0, padx=5, pady=5)
        more_less_label = Label(betting_sheet_frame, text="More/Less", font=("Arial", 12, "bold"), bg="#2C2F33", fg="#FFFFFF")
        more_less_label.grid(row=0, column=1, padx=5, pady=5)

        # Create line groups based on the betting sheets
        max_players_per_line = 6
        for idx, sheet in enumerate(self.betting_sheets, start=1):
            # Create a label for the line number
            line_number_label = Label(betting_sheet_frame, text=f"Line {idx}", font=("Arial", 12), bg="#2C2F33", fg="#FFFFFF")
            line_number_label.grid(row=idx * (max_players_per_line + 2), column=0, padx=5, pady=5, sticky="w")

            # Create a label for the More/Less column
            more_less_label = Label(betting_sheet_frame, text="", font=("Arial", 12), bg="#2C2F33", fg="#FFFFFF")
            more_less_label.grid(row=idx * (max_players_per_line + 2), column=1, padx=5, pady=5, sticky="w")

            # Display chosen player names and their More/Less values under each line header
            for j, (player, is_less) in enumerate(sheet, start=1):
                player_label = Label(betting_sheet_frame, text=player, font=("Arial", 12), bg="#2C2F33", fg="#FFFFFF")
                player_label.grid(row=idx * (max_players_per_line + 2) + j, column=0, padx=5, pady=5, sticky="w")

                # Determine More/Less value based on the choice (reverse the logic)
                more_less_value = "More" if is_less else "Less"

                # Create a label for the More/Less value
                more_less_player_label = Label(betting_sheet_frame, text=more_less_value, font=("Arial", 12), bg="#2C2F33", fg="#FFFFFF")
                more_less_player_label.grid(row=idx * (max_players_per_line + 2) + j, column=1, padx=5, pady=5, sticky="w")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    PlayerStatsGUI().run()
