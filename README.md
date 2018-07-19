# yt-metadata
Script to import [youtube-dl](https://github.com/rg3/youtube-dl) metadata to PostgreSQL.    
The actual `.jpg` files for the thumbnails are saved into the database as byte arrays (Only the **default** 
thumbnail saved by **youtube-dl**)

### Scraping metadata using youtube-dl
This tool expects the files to be in the format that this bash script will output:
```bash
id="$1"
mkdir "$id"; cd "$id"
youtube-dl -v --print-traffic --restrict-filename --write-description --write-info-json --write-annotations --write-thumbnail --all-subs --write-sub --skip-download --ignore-config --ignore-errors --geo-bypass --youtube-skip-dash-manifest https://www.youtube.com/watch?v=$id
```

### Setup instructions:
* Create the database and schema with the tool of your choice using `schema.sql`
* Change the directory in `import.py` so it points to the location of your youtube metadata
* Run `import.py`

### Schema:
![schema](https://user-images.githubusercontent.com/7120851/42967825-72bc88fe-8b6f-11e8-81a7-f8e7e17077d8.png)
