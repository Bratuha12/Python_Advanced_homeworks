from celery import shared_task

# 5: 1 * 2 * 3 * 4 * 5 = 120
@shared_task
def fac(n):
    for x in range(1, n):
        n *= x
    return n


# 1, 1, 2, 3, 5, 8
@shared_task
def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)
