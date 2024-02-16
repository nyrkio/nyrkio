import os
import sentry_sdk


def profiles_sampler(sampling_context):
    # ...
    # return a number between 0 and 1 or a boolean
    return True


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    enable_tracing=True,
    # To set a uniform sample rate
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production,
    profiles_sample_rate=1.0,
    # Alternatively, to control sampling dynamically
    profiles_sampler=profiles_sampler,
)
