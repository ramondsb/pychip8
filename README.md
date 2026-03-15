# PyChip8

## What is it?

Another Chip8 emulator implementation in Python

![Interpreting the MAZE ROM](./running_maze.gif)

## Table of Contents

* [Why have I created this?](#why-have-i-created-this-?)
* [Dependencies](dependencis)
* [How to run](#how-to-run)
* [How to test](#how-to-test)
* [Resources](#resources)
* [License](#license)

## Why have I created this?

- Just for fun!
- To learn more about Python and Emulators
- To create a portfolio (~~to impress recruiters~~)
- To help  interested in coding an emulator with another reference material
- ~~To pollute Github with another crap repository~~

## Dependencies

- _Python >= 3.6_
- _Pygame == 1.9_

## How to run

### Get access to some ROMs

There are public domain ROMs [here](https://www.zophar.net/pdroms/chip8.html).

### Run program
```shell
python pychip8/Emulator "ROM file"
```

## How to test

### Unit Tests
```shell
python3 -m unittest discover -s tests
```

## Resources

* [Tutorial by Multigesture](http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)
* [ROMs by Zophar](https://www.zophar.net/pdroms/chip8.html)

## LICENSE

MIT License

Checkout the LICENSE file in the root directory