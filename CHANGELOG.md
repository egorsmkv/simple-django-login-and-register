# Change log

## v2.19

- Updated Django to 2.2.27

## v2.18

- Added French translation by @tidji31

## v2.17

- Updated Django to 2.2.20

## v2.16

- Updated Django to 2.2.12
- Fixed a bug with decoding UID on the restore password page (#71)

## v2.15

- Updated Django to 2.2.11

## v2.14

- Updated Django, django-bootstrap4, Bootstrap, popper.js, and jQuery to their latest versions

## v2.13

- Updated Django to 2.1.2 version (this version has a vulnerability fix)

## v2.11

- Added the "remember me" checkbox to the log in page
- Added the username recovering
- Code improvements

## v2.10

- Removed i18n_patterns from urls.py
- Added the GuestOnlyView for checks on pages like SignInView, SignUpView, etc
- Removed gunicorn from dependencies
- Updated Django to 2.0.5
- Updated Bootstrap to 4.1.1, jQuery to 3.3.1, PopperJS to 1.14.3

## v2.9

- Updated Bootstrap to 4.1.0 version

## v2.8

- Updated Django to 2.0.4 version
- Added the support to serve media files in debug mode

## v2.7

- Added the pipenv & cleaned up the readme

## v2.6

- Updated Django to 2.0.3 version
- Fixed a bug with the incorrect query in forms. Thanks [karanrajpal14][3] ([#33][4])

## v2.5

- Updated Bootstrap to 4.0.0 version & updated django-bootstrap4 dependency
- Updated Django to 2.0.2 version
- Renamed zh_Hans to zh_hans locale

## v2.4

- Added the Simplified Chinese translation by [hanwentao][1] ([#27][2])

## v2.3

- Added translations for Ukrainian, Russian, Spanish, French, and German languages

## v2.2

- Changed straight call of User's model
- Added the profile editing
- Added email changing
- Changed validation handles
- Improve sign in view
- Renamed SignInViaEmailOrForm to SignInViaEmailOrUsernameForm

## v2.1

- Revised the readme
- Fixed some bugs and added a few improvements

## v2.0

- Add password reset by a username
- Add authentication by email
- Add check for unique email on sign up step
- Add a profile activation
- Update Bootstrap to the v4.0.0-beta.2 version
- Replace mysql database to sqlite
- Many other improvements

## v1.0

Initial version.


[1]: https://github.com/hanwentao
[2]: https://github.com/egorsmkv/simple-django-login-and-register/pull/27
[3]: https://github.com/karanrajpal14
[4]: https://github.com/egorsmkv/simple-django-login-and-register/issues/33
