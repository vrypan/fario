# Examples

Here are some quick scripts to illustrate how `fario` can be used.

## Extract all links by user
Extract all links shared (as embeds) by a user:

```
fario-out --casts $(fario-fid-byname vrypan.eth) | \
fario2json | \
jq ' .. | objects.url | select( . != null )'
```

## Get a user's cast activity by month

```
fario-out --casts $(fario-fid-byname vrypan.eth) | \
  fario2json | \
  jq '.[].data.timestamp' | \
  sort -r | \
  xargs -L1 -I {} dc -e "{} 1609459200 + p"  | \
  xargs -L1 -I{}  date -r {} +"%Y-%m" | \
  uniq -c

 282 2023-10
 271 2023-09
  55 2023-08
  24 2023-07
  12 2023-06
   4 2023-05
  11 2023-04
  39 2023-03
  85 2023-02
  44 2023-01
   9 2022-12
  46 2022-11
  72 2022-10
  20 2022-09
  26 2022-08
  10 2022-07
  ```

  Note: we have to add 1609459200 to farcaster dates to get unix timestamps.

  Let's chart the data using [termgraph](https://github.com/mkaz/termgraph)

  ```
  fario-out --casts $(fario-fid-byname vrypan.eth) | \
  fario2json | \
  jq '.[].data.timestamp' | \
  sort -r -n | \
  xargs -L1 -I {} dc -e "{} 1609459200 + p"  | \
  xargs -L1 -I{}  date -r {} +"%Y-%m" | \
  uniq -c | \
  awk '{ print $2, $1}' | termgraph --format='{:.0f}'

2024-09: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 198
2024-08: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 414
2024-07: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 283
2024-06: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 375
2024-05: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 234
2024-04: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 191
2024-03: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 233
2024-02: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 596
2024-01: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 504
2023-12: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 425
2023-11: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 324
2023-10: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 448
2023-09: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 271
2023-08: ▇▇▇▇ 55
2023-07: ▇▇ 24
2023-06: ▇ 12
2023-05: ▏ 4
2023-04: ▏ 11
2023-03: ▇▇▇ 39
2023-02: ▇▇▇▇▇▇▇ 85
2023-01: ▇▇▇ 44
2022-12: ▏ 9
2022-11: ▇▇▇ 46
2022-10: ▇▇▇▇▇▇ 72
2022-09: ▇ 20
2022-08: ▇▇ 26
2022-07: ▏ 10
```

## Users that followed me, per month

```
fario-out --inlinks $(fario-fid-byname vrypan.eth) | \
fario2json | \
jq '.[].data.timestamp' | \
sort -r -n | \
xargs -L1 -I {} dc -e "{} 1609459200 + p"  | \
xargs -L1 -I{}  date -r {} +"%Y-%m" | \
uniq -c | \
awk '{ print $2, $1}' | termgraph --title "Followed me" --width=20 --format='{:.0f}'

# Followed me

2023-10: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 177
2023-09: ▇▇▇▇▇▇▇▇▇▇▇▇ 108
2023-08: ▇ 16
2023-07: ▇▇ 22
2023-06: ▏ 5
2023-05: ▏ 3
```