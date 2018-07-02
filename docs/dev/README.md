

http://aiosmtpd.readthedocs.io/en/latest/aiosmtpd/docs/controller.html

for i in `seq 1 50`;do echo "foo" | mailx -S smtp=smtp://localhost:10025 -s "hello foo $i" jojo@terhaak.de; done


https://packages.ubuntu.com/bionic/python3-aiosmtpd

https://packages.debian.org/stretch-backports/python3-aiosmtpd
