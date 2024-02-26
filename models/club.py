class Club:

    def __init__(self, club_id, name, slug, abbreviation, display_name, short_display_name, location, league, players_url):

        self.club_id = club_id
        self.name = name
        self.slug = slug
        self.abbreviation = abbreviation
        self.display_name = display_name
        self.short_display_name = short_display_name
        self.location = location
        
        self.league = league
        self.players_url = players_url

# Club class