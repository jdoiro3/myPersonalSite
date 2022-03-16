# myPersonalSite

This Django project currently only holds one app: my personal blog. The blog is hosted [here](https://joseph-doiron-blog.herokuapp.com/). I'm planning on adding additional apps to this site in the future.

## Technologies Used

- **[Django](https://www.djangoproject.com/)**: Python based web framework.
- **[AWS S3 Bucket](https://en.wikipedia.org/wiki/Amazon_S3)**: Bucket stores media files (e.g., post images) and the [Inverted Index]() within a json file.
- **[Heroku](https://en.wikipedia.org/wiki/Heroku)**: Site hosting service. A free tier Dyno is used with a PostgreSQL database.

# Blog

My personal blog site was created mainly to learn Web Development and improve my written communication. I dedicated two posts (part 1 found [here](https://joseph-doiron-blog.herokuapp.com/post/making-a-blog-part-1/)) to making the site. Posts are written in Markdown, with some HTML tags allowed as well.

## Blog Features

- **Full Text-Searches**: The feature is implemented with an in-memory Python dictionary (i.e., Hash Table). The dictionary is part of the *InvertedIndex* object and the source code for the index is found in [index.py](/modules/index.py). The Heroku Dyno that runs my app in the cloud is killed after one hour of no traffic, which means the in-memory index is lost. This is handled by writing the index to a json file in S3 whenever the state changes.

- **Post Editing**:

    - Markdown Editor:

    - Uploaded Image Management:

    - Blockquotes:

