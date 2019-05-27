# Browser support measurer

Enter the browser versions you plan to support and this script will tell you what percentage of users will be supported. You can then tweak the versions you support with reference to [Can I use's usage table](https://caniuse.com/usage-table) and also what features you need.


## Example

Browser versions and regions are specified in a config file and shown next to the browser names below (also has pretty colors when executed).

```
~/browser_support$ pipenv run python stats.py --sort-region GB
Region                        Global              US              GB

Browser (total, support)
iOS Safari (10.3+)              9.2%    8.9%   33.4%   32.4%   31.0%   30.1%
Chrome for Android* (57+)      30.8%   30.8%   29.5%   29.5%   27.3%   27.3%
Chrome (57+)                   33.8%   32.3%   16.5%   15.8%   18.2%   17.6%
Samsung Internet                3.3%       ?    2.5%       ?    4.3%       ?
Edge (17+)                      2.2%    2.0%    2.3%    2.1%    2.8%    2.5%
Safari (10.1+)                  3.2%    2.6%    2.3%    2.2%    2.5%    2.4%
Firefox (52+)                   5.0%    4.5%    2.5%    2.2%    2.4%    2.3%
IE (None+)                      2.7%    0.0%    2.7%    0.0%    2.1%    0.0%
Android Browser                 0.5%       ?    0.6%       ?    0.7%       ?
Opera                           1.4%       ?    0.2%       ?    0.4%       ?
Firefox for Android* (52+)      0.2%    0.2%    0.2%    0.2%    0.2%    0.2%
Opera Mini* (None+)             1.4%    0.0%    0.2%    0.0%    0.2%    0.0%
IE Mobile (None+)               0.1%    0.0%    0.1%    0.0%    0.1%    0.0%
UC Browser for Android*         3.1%       ?    0.2%       ?    0.1%       ?
Blackberry Browser              0.0%       ?    0.0%       ?    0.0%       ?
QQ Browser                      0.1%       ?    0.0%       ?    0.0%       ?
Opera Mobile                    0.0%       ?    0.0%       ?    0.0%       ?
Baidu Browser*                  0.0%       ?    0.0%       ?    0.0%       ?
KaiOS Browser                   0.4%       ?    0.0%       ?    0.0%       ?

Total
Supported                              81.2%           84.5%           82.4%
Unknown                                11.3%           10.3%           13.2%
Not supported                           7.4%            5.2%            4.4%

* No version tracking (any kind of support will match all versions)
```


## Setup

Prerequisites: `pipenv` and `python3.6+`

 1. `pipenv install`
 2. `cp config.py.template config.py` (and tweak)
 3. `pipenv run python stats.py --download`

Future invocations do not require `--download`. You can also use `--sort-region` to sort by a region other than "Global".


## Credits

Downloads data from [caniuse.com](https://caniuse.com) which in turn uses third-party sources.
