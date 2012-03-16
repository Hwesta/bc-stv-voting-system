from django.shortcuts import render_to_response
from ridings.models import Riding

# TODO Add decorators limiting access

# Candidate/Incumbent Information
# NOTE Should we have one set of functions for incumbents and candidates,
# and just display different info based on a flag?

