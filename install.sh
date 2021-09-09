#!/bin/sh -e
#
# Robot Music Box install script
#
#   Copyright (C) 2021 Yoichi Tanibayashi
#
############################################################
help() {
    cat <<'END'

[インストール後のディレクトリ構造]

 $HOME/ ... ホームディレクトリ
    |
    +- bin/ .. BINDIR シェルスクリプトなど
    |   |
    |   +- Ytani_Tcpcmd .. WRAPPER_SCRIPT
    |   +- boot-Ytani_Tcpcmd.sh .. 起動スクリプト
    |
    +- ytani_tcpcmd/ .. WORKDIR
    |   |
    |   +- log/
    |   |
    |   +- webroot/ .. WEBROOT
    |   |   |
    |   |   +- templates/
    |   |   +- static/
    |   |       |
    |   |       +- css/
    |   |       +- js/
    |   |       +- images/
    |   |       :
    |   |
    |   +- upload/
    |   +- data/
    |   :
    |
    +- env1/ .. python3 Virtualenv(venv) 【ユーザが作成する】
        |
        +- ytani_tcpcmd_repo1/ .. MYDIR
        |   |
        |   +- build/ .. BUILD_DIR
        |
        +- subpackage1/
        |
        :

END
}

############################################################
MYNAME=`basename $0`
cd `dirname $0`
MYDIR=`pwd`
echo "MYDIR=$MYDIR"


MY_PKG="ytani_tcpcmd"
WRAPPER_SCRIPT="ytani_tcpcmd"


echo "MY_PKG=$MY_PKG"
echo "WRAPPER_SCRIPT=$WRAPPER_SCRIPT"

BINDIR="$HOME/bin"
BINFILES=

WRAPPER_SRC="$WRAPPER_SCRIPT.in"
echo "WRAPPER_SRC=$WRAPPER_SRC"

PKGS_TXT="pkgs.txt"

BUILD_DIR="$MYDIR/build"

INSTALLED_FILE="$BUILD_DIR/installed"

FAST_MODE=0

echo
#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

install_external_python_pkg() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### install/update $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo ./$_DIR
    git pull
    pip install .
    echo
}

usage() {
    echo
    echo "  Usage: $MYNAME [-u] [-h]"
    echo
    echo "    -f  fastmode"
    echo "    -u  uninstall"
    echo "    -h  show this usage"
    echo
}

uninstall() {
    cd_echo $MYDIR

    if [ -f $INSTALLED_FILE ]; then
        echo "### remove installed files"
        echo
        rm -f `cat $INSTALLED_FILE`
        echo
    fi

    echo "### uninstall my python package"
    echo
    pip uninstall -y $MY_PKG
    echo

    echo "### remove build/"
    echo
    rm -rfv build
}

#
# main
#
cd_echo $MYDIR
MY_VERSION=`python setup.py --version`
echo "MY_VERSION=$MY_VERSION"
echo

while getopts fuh OPT; do
    case $OPT in
        f) FAST_MODE=1;echo "FAST_MODE=$FAST_MODE";;
        u) uninstall; exit 0;;
        h) usage; help; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

#
# install Linux packages
#
if [ -f $PKGS_TXT ]; then
    PKGS=`cat $PKGS_TXT`
    if [ ! -z $PKGS ]; then
        echo "### install Linux packages"
        echo
        sudo apt install `cat $PKGS_TXT`
        echo
    fi
fi

#
# venv
#
if [ -z $VIRTUAL_ENV ]; then
    while [ ! -f ./bin/activate ]; do
        cd ..
        if [ `pwd` = "/" ]; then
            echo
            echo "ERROR: Please create and activate Python3 Virtualenv(venv) and run again"
            echo
            echo "\$ cd ~"
            echo "\$ python -m venv env1"
            echo "\$ . ~/env1/bin/activate"
            echo
            exit 1
        fi
    done
    echo "### activate venv"
    . ./bin/activate
fi
cd_echo $VIRTUAL_ENV

#
# make $WRAPPER_SCRIPT
#
cd_echo $MYDIR

if [ -f $WRAPPER_SRC ]; then
    if [ ! -d $BUILD_DIR ]; then
        mkdir -pv $BUILD_DIR
        echo -n > $INSTALLED_FILE
    fi

    echo "### build $WRAPPER_SCRIPT"
    sed -e "s?%%% MY_PKG %%%?$MY_PKG?" \
        -e "s?%%% MY_VERSION %%%?$MY_VERSION?" \
        -e "s?%%% VENVDIR %%%?$VIRTUAL_ENV?" \
        -e "s?%%% WORKDIR %%%?$WORKDIR?" \
        -e "s?%%% WEBROOT %%%?$WEBROOT?" \
        $WRAPPER_SRC > $BUILD_DIR/$WRAPPER_SCRIPT

    chmod +x $BUILD_DIR/$WRAPPER_SCRIPT
    echo $BUILD_DIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE

    echo '-----'
    cat $BUILD_DIR/$WRAPPER_SCRIPT | sed -n -e '1,/\#* main/p'
    echo '  :'
    echo '-----'
    echo

    
    BINFILES="$BINFILES $BUILD_DIR/$WRAPPER_SCRIPT"    
fi

#
# install scripts
#
echo "### install script files to $BINDIR"
echo
if [ ! -z $BINFILES ]; then
    if [ ! -d $BINDIR ]; then
        mkdir -pv $BINDIR
    fi
    for f in $BINFILES; do
        cp -fv $f $BINDIR
    done
fi
echo

#
# update pip, setuptools, and wheel
#
if [ $FAST_MODE -eq 0 ]; then
    echo "### insall/update pip etc. .."
    echo
    pip install -U pip setuptools wheel
    hash -r
    echo
    pip -V
    echo
fi

#
# install my python packages
#
#if [ $FAST_MODE -eq 0 ]; then
#    install_external_python_pkg $CUILIB_PKG $CUILIB_DIR $CUILIB_GIT
#fi

#
# install my package
#
cd_echo $MYDIR
echo "### install my python package"
echo
pip install .
echo
