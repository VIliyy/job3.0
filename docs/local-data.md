# Local Data and Privacy

This project keeps personal data on the local machine. The clean Git release contains code, tests, and example configuration only.

## Files intentionally excluded from Git

- `backend/.env`: API keys, bridge tokens, and local runtime settings.
- `backend/data/`: toolbox configuration and video-note data.
- `backend/uploads/`: resumes, audio, video, and other uploaded files.
- `backend/job3.db` and `job3.db`: local SQLite databases.
- Logs, coverage reports, temporary screenshots, and browser-extension packages.

These paths are ignored by `.gitignore` and are not needed for a clean source checkout.

## Keeping data for the next local run

Do not delete the ignored files when updating the source. Pulling or switching Git commits does not remove them. The next local run will continue using the same `.env`, database, uploads, and `backend/data/` files.

## Moving to another computer

The clean repository intentionally does not sync personal data. Before moving machines, make a private backup of the ignored paths above. After cloning the repository, install dependencies, restore those paths, and then start the backend and frontend.

Never commit the backup archive to this repository or upload it to a public release.
