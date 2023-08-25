#1 - Getting started
One simple way to check if seahorse was correctly installed is to do the following command line:

```shell
python main_tictac.py -t local -g 1 random_player_tictac.py alpha_player_tictac.py   
```
A graphic interface should then appear in your browser.

|Initial state|Intermediate state|Final state|
|:-:|:-:|:-:|
|![](../assets/tictac_init.png)|![](../assets/tictac_state.png)|![](../assets/tictac_final.png)|

seahorse is the perfect framework to facilitate the implementation of adversarial agents. It helps developper to focus only on the very specific mecanic of the environment in which their agent will evolve. You don't lose time on game logic or execution facilities anymore. It has several features which includes for example a multi-level log system, a game recorder, a responsive GUI,.

![](../assets/logs.png)
