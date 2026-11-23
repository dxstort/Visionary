# Visionary

## Pause & Play videos (`pause_and_play/`)

**Standing rule: when a video is finished, publish it as a GitHub Release with the mp4 and thumbnail attached.**
Also send the finished mp4 (and thumbnails) to the user in the chat so they can download it from their phone.

Steps once a video is rendered and verified (ffprobe, full decode, −14 LUFS, a frame per shot checked):

1. Make the thumbnails with `<story>_thumbnail.py`: `out/<story>_thumbnail_vertical.png` (1080x1920) and
   `out/<story>_thumbnail.png` (1280x720).
2. Write a kid-friendly YouTube title and description.
3. Add `pause_and_play/releases/NN_<story>.json`. NN is the next number, so the newest video sorts last and
   becomes the "latest" release. Fields: `tag`, `story`, `title`, `description`, `video`, `thumbnails`
   (copy an existing manifest).
4. Commit the mp4, the thumbnails and the manifest, then push. `.github/workflows/release-video.yml` creates
   the release, with the release name as the title, the body as the description, and the mp4 and thumbnails
   attached. A video that already has a release is skipped.
5. Send the mp4 and thumbnails to the user with SendUserFile, and give the release link
   (`https://github.com/dxstort/Visionary/releases/tag/<tag>`).

Another tool ("Jarvis") watches the latest release and uploads it to YouTube, so the title, description and
thumbnail in the release must be final.
