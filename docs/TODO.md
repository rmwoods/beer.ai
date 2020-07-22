* Home Page
  * Splash layout with wide image
  * Links to most recent things (posts and apps?)
  * Set pagination
  * Link to github?
  * Rob
* Posts
  * List of posts from most recent backwards
	 - Already done?
  * If post has image, a thumbnail of image
	  - modified `_includes/archive-single.html` to include thumbnail image. Included an example post `2020-07-13-this-is-my-kettle.md` showing how to specify the _teaser_ image. Also, a site-wide default teaser can be set in `_config.yml`. Added a directory `images` to line-up with the documentation for minimal mistakes.
  * Share, comment, Author(s), read time?
      - **read time** is already there
      - **Comments**: Need to decide on a 3rd-party service for this (disqus, discourse, facebook), utterances https://utteranc.es/, or staticman https://staticman.net/docs/. Downside of 3rd-party system is that we don't own comments (so we could lose them at some point), there could be others. Staticman lets us control the comments, but we need to allow staticman push access to the repo. If you set `moderation: true` in the `staticman.yml` file (goes in the root of the repo), then you get pull requests when a comment is submitted. Utterances uses github issues as its mechanism. It requires that people leaving comments have a github account, as far as I can tell. See https://mmistakes.github.io/minimal-mistakes/docs/configuration/. Finally, comments will only be shown if `JEKYLL_ENV=production` (see https://jekyllrb.com/docs/step-by-step/10-deployment/#Environments)
      - **Share**: If you’d like to add, remove, or change the order of these default links you can do so by editing `_includes/social-share.html`. I added a reddit share button.
      - **Authors**: Multiple authors are not supported, and probably won't ever be. https://github.com/mmistakes/minimal-mistakes/issues/1341 and https://github.com/mmistakes/minimal-mistakes/issues/2564 Easiest suggestion would be to make "authors" that are groups e.g. _Rob and Rory_ or _Compubeerers_ in `_data/authors.yml`
  * Aaron
* Apps
  * Is there a way to disable the side bar but keep the grid?
    * Figured out how to do it in ALL pages, how to do with parameter?
  * Can we set the number of columns in the grid?
    * Figured out how to do it by hand in the sass file. Can we do it with a parameter?
  * Is there a way to control the app ordering?
