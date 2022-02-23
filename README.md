# Mendeley → BibTeX
I knocked up this script this afternoon, since I realised that with Mendeley moving from their native desktop app (Mendeley Desktop) to their web app (Mendeley Reference Manager), there may come a time when their native BibTeX exporter functionality is no longer available. If you prefer not to use the desktop app anyway, it's also useful (I personally quite like using PaperShip, since the iPad version can run on my M1 mac)

The app is pretty simple, it just creates and manages an OAuth token, refreshes it if needed and pickles the token object between runs (yeah I know it's not the most secure...). From this it just calls the Mendeley API which returns the entires as BibTeX entries.

Since the API is limited ot a maximum of 500 citations, if it detects that there's more than 499 refs, it cycles through each of the folders and makes sures that it's not doubling up on entries, by using the citation key as an index. if there's \<= 499 refs, then it can one-shot them down!

See, VERY simple :)

If you're going to use this yoiurself, make sure to set the location where you want the pickled token to go as `authFile`, and your `.bib` file as `bibFile`.

I'm not sure if my app ID will work for you, but if not, create a new one for yourself at the [Mendeley dev portal](https://dev.mendeley.com/myapps.html) and create an app for yourself. The redirect URL can be anything but `http://localhost:5000/oauth` is what I've used in here. Once you have a new client ID, client secret and redirect URL (if you went with a different one), be sure to update them in the `TokenClass` `__init__` function.