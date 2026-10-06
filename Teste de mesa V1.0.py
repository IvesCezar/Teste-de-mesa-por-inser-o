from pathlib import Path
import webbrowser


def main():
	app_path = Path(__file__).with_name("index.html")
	webbrowser.open(app_path.resolve().as_uri())


if __name__ == "__main__":
	main()