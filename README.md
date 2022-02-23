# Mendeley → BibTeX
I knocked up this script this afternoon, since I realised that with Mendeley moving from their native desktop app (Mendeley Desktop) to their web app (Mendeley Reference Manager), there may come a time when their native BibTeX exporter functionality is no longer available. If you prefer not to use the desktop app anyway, it's also useful (I personally quite like using PaperShip, since the iPad version can run on my M1 mac)

The app is pretty simple, it just creates and manages an OAuth token, refreshes it if needed and pickles the token object between runs (yeah I know it's not the most secure...). From this it just calls the Mendeley API which returns the entires as BibTeX entries.

Since the API is limited ot a maximum of 500 citations, it cycles through each of the folders and makes sures that it's not doubling up on entries, by using the citation key as an index.

See, VERY simple :)
