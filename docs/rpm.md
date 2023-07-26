# How to create a RPM package

## Build the package

```
rpmbuild  -bb --target aarch64 "./rpm/spec/swu-client.spec"
```

The generated RPM package will be located at `./rpm/aarch64/`

__Note:__ The above command can be run on EXMU-X261 or your x86_64 development machine.
But in case of the latter, you need to first source our SDK script.


## Install the package

To install the RPM package, run the following command on EXMU-X261.

```
sudo dnf install <path to the RPM package>
```
