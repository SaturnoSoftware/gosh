# gosh

**Made with <3 by [mateus.digital](https://mateus.digital)**

<!-- ----------------------------------------------------------------------- -->
<p align="center">
  <a href="https://mateus.digital/gosh">
    <img style="border-radius: 10px;" src="https://raw.githubusercontent.com/mateusdigital/gosh/refs/heads/master/_project-resources/readme.gif"/>
  </a>
</p>

<!-- Badges -->
[![Latest release](https://img.shields.io/github/v/tag/mateusdigital/gosh?label=Latest%20release&style=for-the-badge)](https://github.com/mateusdigital/gosh/releases)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/t/mateusdigital/gosh?style=for-the-badge)](https://github.com/mateusdigital/gosh/commits)
[![Stars](https://img.shields.io/github/stars/mateusdigital/gosh?style=for-the-badge)](https://github.com/mateusdigital/gosh/stargazers)
![GitHub License](https://img.shields.io/github/license/mateusdigital/gosh?style=for-the-badge)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fmateus.digital%2Fgosh&style=for-the-badge&logo=web)](https://mateus.digital/gosh)

<!-- ----------------------------------------------------------------------- -->
## Description:

`gosh` is a simple Bash bookmark utility that lets you jump between frequently used directories quickly.  
It reduces the stress of traversing long, nested paths or places that you reference often.

It works as a lightweight CLI companion powered by python, with hooks in bash and powershell..

As usual, you are very welcomed to share and hack it, and I would love to hear feedback if you have any.

---

## Usage:

```
Usage:
  gosh                   (Same as gosh -l)
  gosh <name>            (To change the directory)
  gosh -h | -v           (Show help | version)
  gosh -l | -L           (Show list of bookmarks)
  gosh -p <name>         (Show path for bookmark)
  gosh -e <path>         (Show bookmark for path)
  gosh -a <name> <path>  (Add bookmark)
  gosh -d <name>         (Delete the bookmark)

Options:
  *-h --help     : Show this screen.
  *-v --version  : Show app version and copyright.

  *-e --exists <path>  : Print the Bookmark for path.
  *-p --print  <name>  : Print the path of Bookmark.

  *-l --list       : Show all Bookmarks (no Paths).
  *-L --list-long  : Show all Bookmarks and Paths.

  *-a --add    <name> <path>  : Add a Bookmark with specified path.
  *-r --delete <name>         : Delete a Bookmark.

Notes:
  If <path> is blank the current directory is assumed.

  Options marked with * are exclusive, i.e. gosh will run that
  and exit after the operation.
```

---

## Installation:

```bash
git clone https://github.com/mateusdigital/gosh
cd gosh

./install.sh  ## if you are in bash
./install.ps1 ## if you are in powershell
```

The same install scripts also work from a packaged release root under
`__DIST/<release-name>/`.

## Build And Package

`gosh` is being aligned to the Saturno.Software shared build contract.

Current repo-level entrypoints:

```powershell
pwsh -File Scripts/build.ps1 -ProjectRoot .
pwsh -File Scripts/package.ps1 -ProjectRoot . -BuildNumber 0
```

Shared Saturno target flow:

```text
spb build
spb package
```

Build outputs are standardized under:

- `__BUILD/<release-name>/`
- `__DIST/<release-name>/`

The packaged release layout is now explicit:

```text
__DIST/<release-name>/
  App/
    gosh2.py
    gosh.sh
    gosh.ps1
  install.sh
  install.ps1
  package.json
  README.md
  ...
```

That keeps the install scripts as the user-facing flow while giving the repo a clearer
package-ready release artifact.

---

## Dependencies:

- python3
- (bash)
- (powershell)

---

<!-- Share -->

[![Share](https://img.shields.io/badge/share-000000?logo=x&logoColor=white)](https://x.com/intent/tweet?text=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/mateusdigital/gosh%20%23cli%20%23productivity)
[![Share](https://img.shields.io/badge/share-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/mateusdigital/gosh)
[![Share](https://img.shields.io/badge/share-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/mateusdigital/gosh)
[![Share](https://img.shields.io/badge/share-FF4500?logo=reddit&logoColor=white)](https://www.reddit.com/submit?title=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/mateusdigital/gosh)
[![Share](https://img.shields.io/badge/share-0088CC?logo=telegram&logoColor=white)](https://t.me/share/url?url=https://github.com/mateusdigital/gosh&text=Check%20out%20this%20project%20on%20GitHub)
[![Star](https://img.shields.io/badge/⭐%20Give%20a%20Star-000000?logo=github&logoColor=white)](https://github.com/mateusdigital/gosh/stargazers)

---

## License:

This software is released under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

---

## Others:

- Email: hello@mateus.digital
- Website: https://mateus.digital
- Itch.io: https://mateusdigital.itch.io
- Linkedin: https://www.linkedin.com/in/mateusdigital
- Twitter: https://www.twitter.com/_mateusdigital
- Youtube: https://www.youtube.com/@_mateusdigital

There is more FLOSS at https://mateus.digital
