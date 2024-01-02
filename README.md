# HyperSpace Points checker

Софт работает асинхронно, но в зависимости от количества проксей. Существует очередь проксей, при которой каждая прокси 
в моменте может быть использована только для одного кошелька. \
Реализовано специально под мобильные прокси что бы на один кошелек был только один айпи.

---

Адреса построчно засунуть в `addresses.txt` и запустить софт `py main.py` в командной строке.

Результат можно увидеть в консоли, и в конце работы софт записывает все результаты в `results.txt`

---

Обычные прокси в `proxies.txt` указывать в формате `http://log:pass@ip:port`. \
Так же можно указывать мобильные прокси в формате 
`http://log:pass@ip:port,https://changeip.mobileproxy.space/?proxy_key=...&format=json`.
> Обычные прокси можно мешать с мобильными, на мобильных будет менять айпи, обычные будет юзать как обычно,
> указывать например так:
> ```
> http://log:pass@ip:port
> http://log:pass@ip:port
> http://log:pass@ip:port,https://changeip.mobileproxy.space/?proxy_key=...&format=json
> http://log:pass@ip:port,https://changeip.mobileproxy.space/?proxy_key=...&format=json
> ```
