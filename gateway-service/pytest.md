- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

---------- coverage: platform linux, python 3.10.14-final-0 ----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/__init__.py                    1      0   100%
app/adapters/__init__.py           2      2     0%   5-7
app/adapters/huaweicloud.py       26     26     0%   5-115
app/bootstrap.py                  35     35     0%   5-79
app/core/__init__.py               7      0   100%
app/core/circuit_breaker.py       80     63    21%   36-45, 62-78, 95-111, 115-125, 129-136, 145-149, 153-157, 166
app/core/discovery.py             69     41    41%   26-31, 48, 62, 76, 89-92, 96-116, 128, 141, 154, 158-159, 167, 185, 190, 195, 205-210
app/core/load_balancer.py         66     48    27%   31-34, 48-65, 78-84, 97-104, 117-133, 145, 155-159
app/core/proxy.py                 55     39    29%   19-22, 26-27, 31, 35-36, 40-41, 53-55, 87-123, 150-166
app/core/retry.py                 43     34    21%   30-34, 51-72, 89-110, 122
app/core/router.py                45     33    27%   22-25, 29-50, 62-76, 89-92, 101, 105-106
app/main.py                       95     95     0%   5-270
app/middleware/__init__.py         5      4    20%   9-13
app/middleware/auth.py            57     56     2%   16-180
app/middleware/logging.py         37     37     0%   5-150
app/middleware/rate_limit.py      59     59     0%   5-174
app/middleware/tracing.py         63     63     0%   5-135
app/models/__init__.py             3      0   100%
app/models/context.py             45     13    71%   62-83
app/models/route.py               37     17    54%   54-65, 77-86
app/settings.py                  143     27    81%   164, 169-171, 183, 193, 203, 213, 223, 253-267, 288-299, 315-317
app/utils/__init__.py              4      0   100%
app/utils/crypto.py               38     21    45%   28-33, 48-49, 59-77, 90-94, 107-111
app/utils/db_init.py              61     47    23%   26-45, 59-93, 107-115, 128-148
app/utils/env_loader.py           85     66    22%   36-52, 66-81, 94-106, 123-149, 166-198, 215-233
------------------------------------------------------------
TOTAL                           1161    826    29%
Coverage HTML written to dir htmlcov

================================================================================== short test summary info ===================================================================================
ERROR tests/test_auth.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
================================================================================ 4 warnings, 1 error in 1.69s ================================================================================

