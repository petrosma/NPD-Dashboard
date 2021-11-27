from numpy.ma.core import count, mean
import streamlit
import streamlit as st
from streamlit import cli as stcli
import sys
import functions
import constants


if __name__ == '__main__':
    if streamlit._is_running_with_streamlit:
        constants.initialize_states()
        functions.sidebar()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())