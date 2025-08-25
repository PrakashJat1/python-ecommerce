from django.contrib import messages
from django.shortcuts import redirect, render


def exception(
    request, exception, exception_view, redirect_to="", render_to="", context={}
):
    print(f"An exception occurred inside {exception_view} ", exception)
    messages.error(request, f"Error inside {exception_view} {exception}")

    if redirect_to != "":
        return redirect(redirect_to)
    elif render_to != "":
        return render(request, render_to, context=context)
    else:
        return redirect(
            request.META.get("HTTP_REFERER", "/")
        )  ## go back to the page where request came from or to home page '/
