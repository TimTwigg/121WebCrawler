<!--
To view this markdown nicely:
    In VSCode, press control+k and then v.
    In other editors, google it.
-->

# 121 Web Crawler ToDo
- Keep track of subdomains and the number of pages per subdomain. I've set up a domains data structure in the frontier. Worker should add domains and subdomains as it encounters them. The domains structure is loaded and saved by `frontier.load_bank()` and `frontier.save_bank()`
- Use robots.txt? Lecture 6.5 slides.
- Detect redirects?

---

# Running the Crawler
The crawler has to be run in openlab since it doesn't even work outside of it. If you run normally, then it will exit when you quit openlab, so you have to use tmux.

<b><u>IMPORTANT</u></b>: tmux sessions exist on a specific host machine in openlab, so if you run tmux, you need to connect to the same machine every time. You achieve this by connecting to a specific ip address rather than openlab.ics.uci.edu (ssh in once, observe the ip, disconnect and change ssh config to connect to that ip instead). Test that you have this working before running the crawler.

### Do the following to run launch.py with tmux:
```
tmux new -s <session name>
```

`Control+b` and then `:` to run a tmux command
```
neww -n <window name>
```

To switch between windows, use `Control+b` to run a tmux command and then hit the number of the window to switch to, eg: `ctrl+b 1`.

```
python launch.py --restart
```

`Control+b d` to detach from tmux without killing it.

Verify that tmux is running with
```
tmux ls
```