
## usage:
## Build the project with dependencies
#      nix-build bepasty-server.nix -A bepasty-server
## Install bepasty-server into environment
#      nix-env -f bepasty-server.nix -iA bepasty-server

# NIX_PATH must contain a valid entry for nixpkgs
with import <nixpkgs> {};

rec {
  bepasty-server = pythonPackages.buildPythonPackage rec {
    name = "bepasty-server";

    propagatedBuildInputs = with pkgs;[
      pythonPackages.flask
      pythonPackages.pygments
      xstatic
      xstatic-bootbox
      xstatic-bootstrap
      xstatic-jquery
      xstatic-jquery-file-upload
      xstatic-jquery-ui
      xstatic-pygments
    ];
    src = ./.;

    meta = {
      homepage = http://github.com/bepasty/bepasty-server;
      description = "binary pastebin server";
      license = stdenv.lib.licenses.mit;
    };
  };

  # The rest are dependencies of bepasty-server
  xstatic-bootbox = pythonPackages.buildPythonPackage rec {
    name = "XStatic-Bootbox-${version}";
    version = "4.3.0.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-Bootbox/XStatic-Bootbox-${version}.tar.gz";
      sha256 = "0wks1lsqngn3gvlhzrvaan1zj8w4wr58xi0pfqhrzckbghvvr0gj";
    };

    meta = {
      homepage =  http://bootboxjs.com;
      description = "bootboxjs packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };

  xstatic-bootstrap = pythonPackages.buildPythonPackage rec {
    name = "XStatic-Bootstrap-${version}";
    version = "3.3.5.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-Bootstrap/XStatic-Bootstrap-${version}.tar.gz";
      sha256 = "0jzjq3d4vp2shd2n20f9y53jnnk1cvphkj1v0awgrf18qsy2bmin";
    };

    meta = {
      homepage =  http://getbootstrap.com;
      description = "bootstrap packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };
  xstatic-jquery = pythonPackages.buildPythonPackage rec {
    name = "XStatic-jQuery-${version}";
    version = "1.10.2.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-jQuery/XStatic-jQuery-${version}.tar.gz";
      sha256 = "018kx4zijflcq8081xx6kmiqf748bsjdq7adij2k91bfp1mnlhc3";
    };

    meta = {
      homepage =  http://jquery.org;
      description = "jquery packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };

  xstatic-jquery-file-upload = pythonPackages.buildPythonPackage rec {
    name = "XStatic-jQuery-File-Upload-${version}";
    version = "9.7.0.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-jQuery-File-Upload/XStatic-jQuery-File-Upload-${version}.tar.gz";
      sha256 = "0d5za18lhzhb54baxq8z73wazq801n3qfj5vgcz7ri3ngx7nb0cg";
    };

    meta = {
      homepage =  http://plugins.jquery.com/project/jQuery-File-Upload;
      description = "jquery-file-upload packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };

  xstatic-jquery-ui = pythonPackages.buildPythonPackage rec {
    name = "XStatic-jquery-ui-${version}";
    version = "1.11.0.1";
    propagatedBuildInputs = [xstatic-jquery];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-jquery-ui/XStatic-jquery-ui-${version}.tar.gz";
      sha256 = "0n6sgg9jxrqfz4zg6iqdmx1isqx2aswadf7mk3fbi48dxcv1i6q9";
    };

    meta = {
      homepage = http://jqueryui.com/;
      description = "jquery-ui packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };

  xstatic-pygments = pythonPackages.buildPythonPackage rec {
    name = "XStatic-Pygments-${version}";
    version = "1.6.0.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic-Pygments/XStatic-Pygments-${version}.tar.gz";
      sha256 = "0fjqgg433wfdnswn7fad1g6k2x6mf24wfnay2j82j0fwgkdxrr7m";
    };
    meta = {
      homepage = http://pygments.org;
      description = "pygments packaged static files for python";
      license = stdenv.lib.licenses.bsd2;
    };
  };

  xstatic = pythonPackages.buildPythonPackage rec {
    name = "XStatic-${version}";
    version = "1.0.1";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/X/XStatic/XStatic-${version}.tar.gz";
      sha256 = "09npcsyf1ccygjs0qc8kdsv4qqy8gm1m6iv63g9y1fgbcry3vj8f";
    };
    meta = {
      homepage = http://bitbucket.org/thomaswaldmann/xstatic;
      description = "packaged static files for python";
      license = stdenv.lib.licenses.mit;
    };
  };
}
