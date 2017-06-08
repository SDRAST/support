#!/usr/bin/env bash

echo "Putting support parent directory on PYTHONPATH"
CURDIR=`pwd`
PARENTDIR="$(dirname ${CURDIR})"

if [[ ${PYTHONPATH} == *${PARENTDIR}* ]]; then
    echo "Parent directory is already on PYTHONPATH"
    exit 0
else
    if [[ -f "${HOME}/.bash_aliases" ]]; then
        BASHFILE="${HOME}/.bash_aliases"
    elif [[ -f "${HOME}/.bashrc" ]]; then
        BASHFILE="${HOME}/.bashrc"
    else
        BASHFILE="${HOME}/.bash_profile"
    fi

    cp ${BASHFILE} "${BASHFILE}_temp"
    PYTHONPATH_STR='${PYTHONPATH}'
    echo "# Added automatically by ${PARENTDIR}/install.sh" >> ${BASHFILE}
    echo "export PYTHONPATH=\"${PYTHONPATH_STR}:${PARENTDIR}\"" >> ${BASHFILE}

fi
echo "Now source your bashrc file!"

