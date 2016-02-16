Title: Draft - File transfer stuff in Perl
Date: 2016-02-13 10:20
Modified: 2016-02-13 10:20
Category: Unix
Tags: perl, file-transfer
Authors: Craig Riley
Summary: Draft - Old perl file transfer stuff

I later moved this whole process to python so I dont even remember if this script worked but hey:

```perl



#!/usr/bin/perl -w
#

use Getopt::Long;


FILE=`ssh prdsftp01.graebel.com "cd /home/ftp_amz/incoming ; ls *gpg"

if [ $FILE ]; then echo "Found a file"; else echo "DID NOT FIND  AFILE"; fi

$ssh = "/usr/bin/ssh";

$scp = /usr/bin/scp";

$ssh_key_file = undef; # might need to define this one day.

$staging_dir = "/var/tmp/staging";

$samba_share = "/home/xfer";

GetOptions(
	"pull_files|p" => \&pull_remote_files,
	"push_files|s" => \&push_files,
	"remote_host|H=s" => \$remote_host,
	"remote_user|u" => \$remote_user,
	"remote_dir|d" => \$remote_dir,
	"grabel_gpg_key|k" => \$key_id,
	"help|h" => \&help);

sub check_local_files
{
	@files = `ls $samba_share/outgoing/`;
	if(@files)
	{
		foreach $
sub check_remote_files
{
@files = `ssh $remote_host "ls $remote_dir/*.gpg"`;

foreach $file(@files)
{
	scp $remote_host:$remote_dir/$file $staging_dir;
	&ck_file_integrity;
}

}
sub ck_file_integrity
{
	## make sure its really a gpg file.
		$file = $_[0];
		$file_type = `$file_cmd $file`;
	
		if($file_type =~ /ASCII text/)
		{

		`chmod 600 $file`;
		&decrypt_file($file);		
											}else
		{
		print "File was not what we expected...logging error."
											$error_level="warn"
		$error_msg = "Something not right about the file..please take a look in staging.\n";
	
		&send_results($error_level,$error_msg);
	
		}
											
										}

sub decrypt_file
{

$file = $_[0];


if(! $key_id )
{
	print "You need to specify a gpg keyfile to use for decryption.\n";
	exit(1);
}else
{
	if(`gpg --default-key $key_id $file > newfilename`
											
	if(`mv newfilename $samba_dir`) 
	{
	$error_level="success";
	$error_msg = "File decrypted and mvoed to share.\n";
	&send_results($error_level,$error_msg);
	}else
	{
	$error_level="error";
	$error_msg = "Failed to decrypt file\n";
	&send_results($error_level,$error_msg);
	}

}
}
sub send_results
{

# buld smtp goodness.

	open(MAIL,"|/usr/bin/mailx") || die "Could not open mail\n";
	print MAIL "To: criley\@graebel.com\n";
	print MAIL "subject: Transfer report\n";
	print MAIL "$error_level \t $error_msg\n";
	print MAIL "\n";
	close(MAIL);
	print MAIL "To:
	$mail = `mailx -s "File Transfer" criley\@graebel.com

}
```
