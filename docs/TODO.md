* Posts
  * About our dataset 
* Findings from Aaron:
      - **Comments**: Need to decide on a 3rd-party service for this (disqus, discourse, facebook), utterances https://utteranc.es/, or staticman https://staticman.net/docs/. Downside of 3rd-party system is that we don't own comments (so we could lose them at some point), there could be others. Staticman lets us control the comments, but we need to allow staticman push access to the repo. If you set `moderation: true` in the `staticman.yml` file (goes in the root of the repo), then you get pull requests when a comment is submitted. Utterances uses github issues as its mechanism. It requires that people leaving comments have a github account, as far as I can tell. See https://mmistakes.github.io/minimal-mistakes/docs/configuration/. Finally, comments will only be shown if `JEKYLL_ENV=production` (see https://jekyllrb.com/docs/step-by-step/10-deployment/#Environments)
      - **Share**: If you’d like to add, remove, or change the order of these default links you can do so by editing `_includes/social-share.html`. I added a reddit share button.
      - **Authors**: Multiple authors are not supported, and probably won't ever be. https://github.com/mmistakes/minimal-mistakes/issues/1341 and https://github.com/mmistakes/minimal-mistakes/issues/2564 Easiest suggestion would be to make "authors" that are groups e.g. _Rob and Rory_ or _Compubeerers_ in `_data/authors.yml`

* Content:
  * Create our icon
  * Import some default images (make a banner?)
  * Define authors, if not already done
  * Look into nbconvert html templates with jinja
    * This is not as straight forward as we expected. There are a few templates available for converting to markdown, but nothing super clean. We probably will need to build something pretty custom since we'd like whatever we export to be consistent with what jekyll builds.
