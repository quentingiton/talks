### Creating a new presentation

  - Create a new branch, make a copy of `template`, and `cd` there
  - git submodule current version of reveal.js
    ```
    $ git submodule add https://github.com/EiffL/reveal.js.git
    $ cd reveal.js
    $ git submodule update --init --recursive
    ```
  - copy `package.json`, `gulpfile.js` from  the `reveal.js` folder to the talk directory
  - Update/install npm modules to make sure it works with this version:
    ```
    $ npm install
    ```
  - Start the server:
    ```
    $ npm start
    ```

At that point, I should be able to see my new presentation in my web browser. I can edit the `index.html` file and my browser should reload when I save it.

If I want to add images and files, I can drop them in the `assets` folder, which will be shared between all of my talks.

When I am satisfied with my talk, I can commit your changes, and push to GitHub.

The last step to publish my talk is to make a Pull Request, to merge my talk branch back to the `main` branch.
