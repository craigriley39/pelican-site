Title: Draft - Nagios Check_sshperf
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: perl, nagios
Authors: Craig Riley
Summary: Draft - check_sshperf

This is a program I used a lot back in the day. Nagios was checking against a bunch of linux and unix machines. The check_sshperf plugin would ssh into a box and run a series of comamnds over the ssh session and then dump them into a named pipe that Nagios would activily listen to. 

Nagios opens a named pipe as part of its processing and uses this to recieve updates on passive checks. Pretty cool when you get to workign with it. 

```perl
#
#   sshperf was hanging due to df -k stating stale NFS mounts. I think it would be best to stat only
#   local filesystems since those are all we are reporting on. changed for solaris df -k to df -lk 
## 
#    - 3/3/05 - craig
##
#   Updated 5/7/09 MAO to handle top upgrade - updated ParseTop() sub
#       Remove dependency on line position of the Memory string, and allow for new labels:
#       Old format:
#        Memory: 16G real, 3798M free, 13G swap in use, 12G swap free
#       New format:
#        Memory: 32G phys mem, 28G free mem, 32G total swap, 32G free swap
##
#############





# die("usage: sshperf -c <configfile>") if ($ARGV[0] != "-c");

$CFGFILE = $ARGV[1];
$SNMPHOST = $ARGV[3];

$LOGFILE = "/usr/local/nagios/var/sshperf.log";
$ECFFILE = "/usr/local/nagios/var/rw/nagios.cmd";
if ($ARGV[0] eq "-d") { $DEBUG = 1; 
} else { $DEBUG = 0; }


## this program:
# reads a config file for thresholds, disks
# collects remote info via ssh
# parses all info into local variables
# submits SSHPERF ok if it can connect via ssh
# for each test in config file, submit passive event to nagios for threshold metrics


## todos:
# error check ARGs
# usage?
#
# collect interface bandwidth usage
# collect disk usage


#######################


my $tests;
&ReadConfig();


if ((!defined($connection{"host"})) || (!defined($connection{"user"})) || (!defined($connection{"key"}))) { die("missing complete connect statement\n"); }


# do the ssh
$SSHCOMMAND = '/usr/bin/ssh';


if ($connection{"host"} =~ /(.*):(\d+)/) {
	$connection{"host"} = $1;
	$connection{"port"} = $2;
}
if (!defined($connection{"osversion"})) { $connection{"osversion"} = "linux-rh"; }

my %commands;
foreach $test (keys(%tests)) {
	# &debug("saw test $test");
	if ($test eq "load-5minave") {
		if (!defined($commands{"uptime"})) { $commands{"uptime"} = 1; }
	} elsif ($test =~ /^proc-exists-/) {
		if (!defined($commands{"ps"})) { $commands{"ps"} = 1; }
	} elsif ($test eq "cpu-idlepct") {
		if (!defined($commands{"vmstat"})) { $commands{"vmstat"} = 1; }
	} elsif ($test eq "mem-free") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			if (!defined($commands{"top"})) { $commands{"top"} = 1; }
		} else {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		}
	} elsif ($test eq "swap-free") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			if (!defined($commands{"top"})) { $commands{"top"} = 1; }
		} else {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		}
	} elsif ($test eq "mem-freepct") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			if (!defined($commands{"top"})) { $commands{"top"} = 1; }
		} else {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		}
	} elsif ($test eq "swap-freepct") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			if (!defined($commands{"top"})) { $commands{"top"} = 1; }
		} else {
			if (!defined($commands{"free"})) { $commands{"free"} = 1; }
		}
	} elsif ($test =~ /^sar-/) {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{"sar"})) { $commands{"sar"} = 1; }
		} else {
			if (!defined($commands{"sar"})) { $commands{"sar"} = 1; }
		}
	} elsif ($test =~ /snmp-oid-/) {
		if (!defined($commands{$test})) { $commands{$test} = 1; }
	} elsif ($test =~ /^snmp-/) {
		if (!defined($commands{$test})) { $commands{$test} = 1; }
	} elsif ($test =~ /disk-usedpct-(.*)/) {
		if (!defined($commands{"df"})) { $commands{"df"} = 1; }
	} elsif ($test =~ /local-check_smtp-(.*)/) {
		if (!defined($commands{$test})) { $commands{$test} = 1; }
	} elsif ($test eq "mysql-status") {
		if (!defined($commands{$test})) { $commands{$test} = 1; }
	} elsif ($test =~ /^int-/) {
		if ($connection{"osversion"} =~ /linux-rh/) {
			if (!defined($commands{$test})) { $commands{$test} = 1; }
		} else { die("cant do interfaces on non-linux: $test\n"); }
	} else { die("unknown test: $test\n"); }
# XXX NEW
}

my $sshcmd = "";
foreach (keys(%commands)) {
	# &debug("registered command $_");
	if ($_ eq "uptime") {
		$sshcmd = $sshcmd . "echo \@\@\@\@;uptime;";
	} elsif ($_ eq "ps") {
		if ($connection{"osversion"} =~ /^solaris-/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;ps -ef;";
		} 
	} elsif ($_ eq "vmstat") {
		$sshcmd = $sshcmd . "echo \@\@\@\@;vmstat 2 2;";
	} elsif ($_ eq "free") {
		$sshcmd = $sshcmd . "echo \@\@\@\@;free;";
	} elsif ($_ eq "top") {
		if ($connection{"osversion"} =~ /^solaris-/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;\/usr\/local\/bin\/top -n 1;";
		} else {
			$sshcmd = $sshcmd . "echo \@\@\@\@;\/usr\/local\/bin\/top;";
		}
	} elsif ($_ eq "df") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;df -P ;";
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;df -lk;";
		} else {
			$sshcmd = $sshcmd . "echo \@\@\@\@;df;";
		}
	} elsif ($_ eq "sar") {
		if ($connection{"osversion"} =~ /linux-rh/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;sar -Ah | sort -n -r -k3 | head -200;";
		} elsif ($connection{"osversion"} =~ /^solaris-/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;perf/collect_stats.pl;";
		} else {
			$sshcmd = $sshcmd . "echo \@\@\@\@;sar -Ah | sort -n -r -k3 | head -200;";
		}
	} elsif ($_ =~ /^local-check_smtp-(.*)/) {
		$sshcmd = $sshcmd . "echo \@\@\@\@;bin/check_smtp -H $1 -w 5 -c 10 -t 10 -e " . $tests{$_}. "$e;";
	} elsif ($_ =~ /^snmp-/) {
		my ($h, $comm, $warn, $crit, $misc) = split("~", $tests{$_});
		if ($SNMPHOST) { $h = $SNMPHOST; }
		if ($_ eq "snmp-winprocessorload") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.2.1.25.3.3.1.2.1;"; 
		} elsif ($_ eq "snmp-winsystemnumusers") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.2.1.25.1.5.0;"; 
		} elsif ($_ eq "snmp-winsystemprocesses") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.2.1.25.1.6.0;"; 
		} elsif ($_ eq "snmp-wintcpcurrestab") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.2.1.6.9.0;"; 
		} elsif ($_ eq "snmp-ioscpu5min") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.4.1.9.2.1.57.0;"; 
		} elsif ($_ eq "snmp-iosmem5minused") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.4.1.9.9.48.1.1.1.5.1;";
		} elsif ($_ eq "snmp-iosmem5minfree") {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h .1.3.6.1.4.1.9.9.48.1.1.1.6.1;";
		} elsif ($_ =~ /snmp-oid-/) {
			$sshcmd = $sshcmd . "echo \@\@\@\@;snmpget -v1 -c $comm -Oq $h $misc;";
		} else {
			die("error: unknown snmp command: $_\n");
		}
	} elsif ($_ eq "mysql-status") {
		my ($user, $pass) = split("~", $tests{$_});
		$sshcmd = $sshcmd . "echo \@\@\@\@;/usr/bin/mysqladmin -u" . $user . " -p" . $pass . " status;";
	} elsif ($_ =~ /^int-(\S+)/) {
		$sshcmd = $sshcmd . "echo \@\@\@\@;grep $1 /proc/net/dev;"; 
	} else { die("unknown command: $_"); }
# XXX NEW
}


$sshline = $SSHCOMMAND . " " . $connection{"host"};
if ($connection{"port"}) { $sshline = $sshline . " -p" . $connection{"port"}; }

$sshline = $sshline . " -l" . $connection{"user"} . " -i" . $connection{"key"};

if ($connection{"extra"}) {
	&debug("Connect extra: " . $connection{"extra"} . "\n");
	$sshline = $sshline .  ' "' . $connection{"extra"} . ' \"' . $sshcmd . ' \" "';
} else {
	$sshline = $sshline .  " \"" . $sshcmd . "\"";
}

&debug("ssh command line: " . $sshline);

$result = `$sshline`;

if ($result =~ /\@\@\@\@/) {
	$SSHPERFstatus = "0"; # 0 = ok, 1 = warn, 2 = crit
	$SSHPERFmessage = ""; # 0 = ok, 1 = warn, 2 = crit
} else {
	$SSHPERFstatus = 2;
	$SSHPERFmessage = "Couldn't connect to " . $connection{"host"};
}

my (@results) = split(/\@\@\@\@/, $result);
my $res = shift(@results); #the first result is trash

foreach (keys(%commands)) {
	$res = shift(@results);
	&debug("Parsing for $_");
	if ($_ eq "uptime") {
		&ParseUptime($res);
	} elsif ($_ eq "ps") {
		&ParsePs($res);
	} elsif ($_ eq "vmstat") {
		&ParseVmstat($res);
	} elsif ($_ eq "free") {
		&ParseFree($res);
	} elsif ($_ eq "df") {
		&ParseDf($res);
	} elsif ($_ eq "top") {
		&ParseTop($res);
	} elsif ($_ eq "sar") {
		&ParseSar($res);
	} elsif ($_ =~ /local-check_smtp-(.*)/) {
		&ParseLocalSmtp($res, $1);
	} elsif ($_ =~ /snmp-oid-/) {
		&ParseSnmpOid($_, $res);
	} elsif ($_ =~ /^snmp-/) {
		&ParseSnmp($_, $res);
	} elsif ($_ =~ /^int-(\S+)/) {
		&ParseInterface($1, $res);
	} elsif ($_ eq "mysql-status") {
		&ParseMysqlStatus($res);
	} else {
		&debug("Unknown command: $_");
		die("Unknown command: $_");
	}
# XXX NEW

}


foreach $test (keys(%tests)) {
	# print "doing result: $test \n";
	# next if ($warn == -1);
	if ($test eq "load-5minave") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"load-5minave"} >= $crit) {
			$ret = 2;
		} elsif ($ans{"load-5minave"} >= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-load-5minave", $ret, "5 minute load is " . $ans{"load-5minave"} . "|load-5minave=" . $ans{"load-5minave"} . ",load-15minave=" . $ans{"load-15minave"});
	} elsif ($test eq "cpu-idlepct") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"cpu-idlepct"} <= $crit) {
			$ret = 2;
		} elsif ($ans{"cpu-idlepct"} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-cpu-idlepct", $ret, "CPU idle time is " . $ans{"cpu-idlepct"} . "%|cpu-idlepct=" . $ans{"cpu-idlepct"} . ",cpu-userpct=" . $ans{"cpu-userpct"} . ",cpu-syspct=" . $ans{"cpu-syspct"});
	} elsif ($test eq "mem-free") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"mem-free"} <= $crit) {
			$ret = 2;
		} elsif ($ans{"mem-free"} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-mem-free", $ret, "Free memory (" . $ans{"mem-free"} . " / " . $ans{"mem-total"} . ") |mem-free=" . $ans{"mem-free"} . ",mem-total=" . $ans{"mem-total"} );
	} elsif ($test =~ /proc-exists-(.*)/) {
		($numprocs, $procname) = split('~', $tests{$test});

		@processes = split /\n/, $ans{"psout"};
		$count = grep /$procname/, @processes;
		
		&debug("proc-exists: Found $count processes \n");

		if ($count < $numprocs) {
			$ret = 2;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-proc-exists-$procname", $ret, "Number of procs with name $procname : " . $count );  
	} elsif ($test eq "swap-free") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"swap-free"} <= $crit) {
			$ret = 2;
		} elsif ($ans{"swap-free"} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-swap-free", $ret, "Free swap (" . $ans{"swap-free"} . " / " . $ans{"swap-total"} . ") |swap-free=" . $ans{"swap-free"} . ",swap-total=" . $ans{"swap-total"} );
	} elsif ($test eq "mem-freepct") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"mem-freepct"} <= $crit) {
			$ret = 2;
		} elsif ($ans{"mem-freepct"} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-mem-freepct", $ret, "Free memory " . sprintf("%02.2f", $ans{"mem-freepct"}) . "% |mem-freepct=" . $ans{"mem-freepct"} );
	} elsif ($test eq "swap-freepct") {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{"swap-freepct"} <= $crit) {
			$ret = 2;
		} elsif ($ans{"swap-freepct"} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-swap-freepct", $ret, "Free swap " . sprintf("%02.2f", $ans{"swap-freepct"}) . "% |swap-freepct=" . $ans{"swap-freepct"} );
	} elsif ($test =~ /disk-usedpct-(.*)/) {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{$test} >= $crit ) {
			$ret = 2;
		} elsif ($ans{$test} >= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		&SubmitPassive("SSHPERF-disk-usedpct-" . $1, $ret, "Space used on filesystem $1: " . sprintf("%02.0f", $ans{$test}) . "% |disk-usedpct-" . $1 . "=" . sprintf("%02.0f", $ans{$test}));
	} elsif ($test =~ /local-check_smtp-(.*)/) {
		if ($ans{$test} == -1) {
			$ret = 2;
			&SubmitPassive("SMTP" , $ret, "Invalid SMTP response");
		} elsif ($ans{$test} == -2) {
			$ret = 2;
			&SubmitPassive("SMTP", $ret, "Connection refused by host");
		} elsif ($ans{$test} < -2) {
			$ret = 2;
			&SubmitPassive("SMTP", $ret, "Unknown error");
		} else {
			$ret = 0;
			&SubmitPassive("SMTP", $ret, "Response time " . $ans{$test} . " seconds");
		}
	} elsif ($test =~ /^snmp-/) {
		if ($test eq "snmp-winprocessorload") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Processor load: " . $ans{$test} . " |winprocessorload=" . $ans{$test});
		} elsif ($test eq "snmp-winsystemnumusers") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Number of users: " . $ans{$test} . " |winsystemnumusers=" . $ans{$test});
		} elsif ($test eq "snmp-winsystemprocesses") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Number of processes: " . $ans{$test} . " |winsystemprocesses=" . $ans{$test});
		} elsif ($test eq "snmp-wintcpcurrestab") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Established TCP sessions: " . $ans{$test} . " |wintcpcurrestab=" . $ans{$test});
		} elsif ($test eq "snmp-ioscpu5min") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "CPU util (5 min ave): " . $ans{$test} . " |cpu5min=" . $ans{$test});
		} elsif ($test eq "snmp-iosmem5minused") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} >= $crit) {
				$ret = 2;
			} elsif ($ans{$test} >= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Mem used (5 min ave): " . $ans{$test} . " |mem5minused=" . $ans{$test});
		} elsif ($test eq "snmp-iosmem5minfree") {
			my ($h, $comm, $warn, $crit) = split("~", $tests{$test});
			if ($ans{$test} <= $crit) {
				$ret = 2;
			} elsif ($ans{$test} <= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			&SubmitPassive($test, $ret, "Mem free (5 min ave): " . $ans{$test} . " |mem5minfree=" . $ans{$test});
		} elsif ($test =~ /snmp-oid-(\S+)/) {
			my $oidname = $1;
			my ($h, $comm, $warn, $crit, $oid) = split("~", $tests{$test});
			if ($ans{$test} <= $crit) {
				$ret = 2;
			} elsif ($ans{$test} <= $warn) {
				$ret = 1;
			} else {
				$ret = 0;
			}
			if ($oidname =~ /\S+-outoctects/) {
				$ans_tmp = $ans{$test};
				$ans_readable = ($ans_tmp/1000) . " k";
			} else {
				$ans_readable = $ans{$test};
			}
			&SubmitPassive($oidname, $ret, $oidname . ": " . $ans_readable . " |" . $oidname . "=" . $ans{$test});
		}
	} elsif ($test =~ /^sar-/) {
		($warn, $crit) = split('~', $tests{$test});
		if ($ans{$test} <= $crit) {
			$ret = 2;
		} elsif ($ans{$test} <= $warn) {
			$ret = 1;
		} else {
			$ret = 0;
		}
		$ret = 0;
		&SubmitPassive("SSHPERF-" . $test, $ret, "$test: $ans{$test} |" . $test . "=" . $ans{$test});
	} elsif ($test eq "mysql-status") {
		($user, $pass, $thread_w, $thread_c, $opent_w, $opent_c, $queries_w, $queries_c) = split('~', $tests{$test});
		if ($ans{"mysql-uptime"} < 0) {
			$ret = 2;
			$string = "Unable to check mysql status";
		} else {
			if ($ans{"mysql-threads"} > $thread_c) {
				$ret = 2;
				&SubmitPassive("SSHPERF-mysql-threads", $ret, "MySQL thread count too high: " . $ans{"mysql-threads"} . "|mysql-threads=" . $ans{"mysql-threads"});
			} elsif ($ans{"mysql-threads"} > $thread_w) {
				$ret = 1;
				&SubmitPassive("SSHPERF-mysql-threads", $ret, "MySQL thread count too high: " . $ans{"mysql-threads"} . "|mysql-threads=" . $ans{"mysql-threads"});
			} else {
				$ret = 0;
				&SubmitPassive("SSHPERF-mysql-threads", $ret, "MySQL thread count okay: " . $ans{"mysql-threads"} . "|mysql-threads=" . $ans{"mysql-threads"});
			}
			if ($ans{"mysql-opentables"} > $opent_c) {
				$ret = 2;
				&SubmitPassive("SSHPERF-mysql-opentables", $ret, "MySQL too many open tables: " . $ans{"mysql-opentables"} . " |mysql-opentables=" . $ans{"mysql-opentables"});
			} elsif ($ans{"mysql-opentables"} > $opent_w) {
				if ($ret < 1) { $ret = 1; }
				&SubmitPassive("SSHPERF-mysql-opentables", $ret, "MySQL too many open tables: " . $ans{"mysql-opentables"} . " |mysql-opentables=" . $ans{"mysql-opentables"});
			} else {
				&SubmitPassive("SSHPERF-mysql-opentables", $ret, "MySQL open tables okay: " . $ans{"mysql-opentables"} . " |mysql-opentables=" . $ans{"mysql-opentables"});
			}
			$string = "Mysql uptime: " . $ans{"mysql-uptime"} . " seconds";
			$string = $string . "|mysql-questions=" . $ans{"mysql-questions"};
		}
		&SubmitPassive("SSHPERF-" . $test, $ret, $string);

	} elsif ($test =~ /^int-(\S+)/) {
		if (defined($ans{$test . "-rxbytes"}) && ($ans{$test . "-rxbytes"} > 1)) {
			$ret = 0;
		} else {
			$ret = 2;
		}
		&SubmitPassive("SSHPERF-" . $test, $ret, "$test |" . $test . "-rxbytes=" . $ans{$test . "-rxbytes"} . "," . $test . "-rxpkts=" . $ans{$test . "-rxpkts"} . "," . $test . "-rxerrs=" . $ans{$test . "-rxerrs"} . "," . $test . "-txbytes=" . $ans{$test . "-txbytes"} . "," . $test . "-txpkts=" . $ans{$test . "-txpkts"} . "," . $test . "-txerrs=" . $ans{$test . "-txerrs"});

	} else { die("error: unknown test type: $test\n"); }
# XXX NEW

}

if ($SSHPERFstatus > 1) {
	&Log("SSHPERF CRITICAL - " . $SSHPERFmessage); print("SSHPERF CRITICAL - " . $SSHPERFmessage . "\n");
	exit(2);
} elsif ($SSHPERFstatus == 1) {  # NOT USED TODAY
	&Log("SSHPERF WARNING - " . $SSHPERFmessage); print("SSHPERF WARNING - " . $SSHPERFmessage . "\n");
	exit(1);
} else {	# ($SSHPERFstatus == 0)
#	&Log("SSHPERF OKAY - " . $SSHPERFmessage); print("SSHPERF OKAY - " . $SSHPERFmessage . "\n");
	&Log("SSHPERF OKAY - SSH to host confirmed\n");
}

exit 0;

#######################

sub ParsePs() {
	my @processes = @_;

	foreach (@processes) {
		$ans{"psout"} .= $_;
	}

}

sub ParseVmstat() {
        my ($line) = @_;
	@lines = split(/\n/, $line);
	&debug("ParseVmstat: parsing: $lines[4]");

	if (($connection{"osversion"} eq "linux-rh") && ($lines[4] =~ /^\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)/)) {
		$ans{"cpu-userpct"} = $1;
		$ans{"cpu-syspct"} = $2;
		$ans{"cpu-idlepct"} = $3;
		&debug("ParseVmstat: found user, sys, idle: $1, $2, $3");
	} elsif (($connection{"osversion"} eq "linux-rh9") && ($lines[4] =~ /^\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+/)) {
		$ans{"cpu-userpct"} = $1;
		$ans{"cpu-syspct"} = $2;
		$ans{"cpu-idlepct"} = $3;
		&debug("ParseVmstat: found user, sys, idle: $1, $2, $3");
	} elsif (($connection{"osversion"} =~ /^solaris-/) && ($lines[4] =~ /^\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)/)) {
		$ans{"cpu-userpct"} = $1;
		$ans{"cpu-syspct"} = $2;
		$ans{"cpu-idlepct"} = $3;
		&debug("ParseVmstat: found user, sys, idle: $1, $2, $3");
	} else {
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse vmstat output."; &Log($SSHPERFmessage);}
	}
}

sub ParseSar() {
        my ($line) = @_;
	# @lines = split(/\n/, $line);

	if ($connection{"osversion"} =~ /linux-rh/) {
		#bull.atrust.com        600     1067843400      -       pgpgin/s        0.00
		my (@tmp) = grep("proc/s", $line);
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+proc\/s\s+(\S+)/) {
			&debug("ParseSar found proc/s: $1");
			$ans{"sar-procs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+cswch\/s\s+(\S+)/) {
			&debug("ParseSar found cswch/s: $1");
			$ans{"sar-cswchs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+intr\/s\s+(\S+)/) {
			&debug("ParseSar found intr/s: $1");
			$ans{"sar-intrs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+pgpgin\/s\s+(\S+)/) {
			&debug("ParseSar found pgpgin/s: $1");
			$ans{"sar-pgpgins"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+pgpgout\/s\s+(\S+)/) {
			&debug("ParseSar found pgpgout/s: $1");
			$ans{"sar-pgpgouts"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+activepg\s+(\S+)/) {
			&debug("ParseSar found activepg: $1");
			$ans{"sar-activepg"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+inadtypg\s+(\S+)/) {
			&debug("ParseSar found inadtypg: $1");
			$ans{"sar-inadtypg"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+inaclnpg\s+(\S+)/) {
			&debug("ParseSar found inaclnpg: $1");
			$ans{"sar-inaclnpg"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+inatarpg\s+(\S+)/) {
			&debug("ParseSar found inatarpg: $1");
			$ans{"sar-inatarpg"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+pswpin\/s\s+(\S+)/) {
			&debug("ParseSar found pswpins: $1");
			$ans{"sar-pswpins"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+pswpout\/s\s+(\S+)/) {
			&debug("ParseSar found pswpouts: $1");
			$ans{"sar-pswpouts"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+tps\s+(\S+)/) {
			&debug("ParseSar found tps: $1");
			$ans{"sar-tps"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+rtps\s+(\S+)/) {
			&debug("ParseSar found rtps: $1");
			$ans{"sar-rtps"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+wtps\s+(\S+)/) {
			&debug("ParseSar found wtps: $1");
			$ans{"sar-wtps"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+bread\/s\s+(\S+)/) {
			&debug("ParseSar found breads: $1");
			$ans{"sar-breads"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+bwrtn\/s\s+(\S+)/) {
			&debug("ParseSar found bwrtns: $1");
			$ans{"sar-bwrtns"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+frmpg\/s\s+(\S+)/) {
			&debug("ParseSar found frmpgs: $1");
			$ans{"sar-frmpgs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+shmpg\/s\s+(\S+)/) {
			&debug("ParseSar found shmpgs: $1");
			$ans{"sar-shmpgs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+bufpg\/s\s+(\S+)/) {
			&debug("ParseSar found bufpgs: $1");
			$ans{"sar-bufpgs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+campg\/s\s+(\S+)/) {
			&debug("ParseSar found campgs: $1");
			$ans{"sar-campgs"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbmemfree\s+(\S+)/) {
			&debug("ParseSar found kbmemfree: $1");
			$ans{"sar-kbmemfree"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbmemused\s+(\S+)/) {
			&debug("ParseSar found kbmemused: $1");
			$ans{"sar-kbmemused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+%memused\s+(\S+)/) {
			&debug("ParseSar found pctmemused: $1");
			$ans{"sar-pctmemused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbmemshrd\s+(\S+)/) {
			&debug("ParseSar found kbmemused: $1");
			$ans{"sar-kbmemused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbbuffers\s+(\S+)/) {
			&debug("ParseSar found kbmemfree: $1");
			$ans{"sar-kbmemfree"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbcached\s+(\S+)/) {
			&debug("ParseSar found kbmemused: $1");
			$ans{"sar-kbmemused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbswpfree\s+(\S+)/) {
			&debug("ParseSar found kbmemfree: $1");
			$ans{"sar-kbmemfree"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+kbswpused\s+(\S+)/) {
			&debug("ParseSar found kbmemused: $1");
			$ans{"sar-kbmemused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+%swpused\s+(\S+)/) {
			&debug("ParseSar found pctswpused: $1");
			$ans{"sar-pctswpused"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+dentunusd\s+(\S+)/) {
			&debug("ParseSar found dentunusd: $1");
			$ans{"sar-dentunusd"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+file-sz\s+(\S+)/) {
			&debug("ParseSar found filesz: $1");
			$ans{"sar-filesz"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+%file-sz\s+(\S+)/) {
			&debug("ParseSar found pctfilesz: $1");
			$ans{"sar-pctfilesz"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+inode-sz\s+(\S+)/) {
			&debug("ParseSar found inodesz: $1");
			$ans{"sar-inodesz"} = $1;
		}
		# super-sz        0
		# %super-sz       0.00
		# dquot-sz        0
		# %dquot-sz       0.00
		# rtsig-sz        0
		# %rtsig-sz       0.00
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+totsck\s+(\S+)/) {
			&debug("ParseSar found totsck: $1");
			$ans{"sar-totsck"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+tcpsck\s+(\S+)/) {
			&debug("ParseSar found tcpsck: $1");
			$ans{"sar-tcpsck"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+udpsck\s+(\S+)/) {
			&debug("ParseSar found udpsck: $1");
			$ans{"sar-udpsck"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+rawsck\s+(\S+)/) {
			&debug("ParseSar found rawsck: $1");
			$ans{"sar-rawsck"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+ip-frag\s+(\S+)/) {
			&debug("ParseSar found ipfrag: $1");
			$ans{"sar-ipfrag"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+runq-sz\s+(\S+)/) {
			&debug("ParseSar found runq-sz: $1");
			$ans{"sar-runqsz"} = $1;
		}
		if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+plist-sz\s+(\S+)/) {
			&debug("ParseSar found plist-sz: $1");
			$ans{"sar-plistsz"} = $1;
		}
		# ldavg-1	0.00
		# if ($line =~ /\S+\s+\S+\s+\S+\s+\S+\s+ldavg-5\s+(\S+)/) {
			# &debug("ParseSar found ldavg-5: $1");
			# $ans{"sar-ldavg5"} = $1;
		# }

	} elsif ($connection{"osversion"} =~ /^solaris-/) {
		@lines = split(/\n/, $line);
		if ($lines[1] =~ /pctusr\s+pctsys\s+pctwio\s+pctidle\s+runqsz.*ovszallocfail\s+fiveminload\s+fifteenminload/) {

			($ans{"sar-pctusr"}, $ans{"sar-pctsys"}, $ans{"sar-pctwio"}, $ans{"sar-pctidle"}, $ans{"sar-runqsz"}, $ans{"sar-pctrunocc"}, $ans{"sar-breads"}, $ans{"sar-lreads"}, $ans{"sar-pctrcache"}, $ans{"sar-bwrits"}, $ans{"sar-lwrits"}, $ans{"sar-pctwcache"}, $ans{"sar-preads"}, $ans{"sar-pwrits"}, $ans{"sar-pswpins"}, $ans{"sar-pswpouts"}, $ans{"sar-bswins"}, $ans{"sar-bswots"}, $ans{"sar-pswchs"}, $ans{"sar-scalls"}, $ans{"sar-sreads"}, $ans{"sar-swrits"}, $ans{"sar-forks"}, $ans{"sar-execs"}, $ans{"sar-rchars"}, $ans{"sar-wchars"}, $ans{"sar-igets"}, $ans{"sar-nameis"}, $ans{"sar-dirbks"}, $ans{"sar-rawchs"}, $ans{"sar-canchs"}, $ans{"sar-outchs"}, $ans{"sar-rcvins"}, $ans{"sar-xmtins"}, $ans{"sar-mdmins"}, $ans{"sar-procsz"}, $ans{"sar-procszmax"}, $ans{"sar-procszov"}, $ans{"sar-inodsz"}, $ans{"sar-inodszmax"}, $ans{"sar-inodszov"}, $ans{"sar-filesz"}, $ans{"sar-fileszmax"}, $ans{"sar-fileszov"}, $ans{"sar-locksz"}, $ans{"sar-lockszmax"}, $ans{"sar-msgs"}, $ans{"sar-semas"}, $ans{"sar-runqsz"}, $ans{"sar-pctrunocc"}, $ans{"sar-pgouts"}, $ans{"sar-ppgouts"}, $ans{"sar-pgfrees"}, $ans{"sar-pgscans"}, $ans{"sar-pctufsipf"}, $ans{"sar-freemem"}, $ans{"sar-freeswap"}, $ans{"sar-smlmem"}, $ans{"sar-smlmemalloc"}, $ans{"sar-smlmemfail"}, $ans{"sar-lgmem"}, $ans{"sar-lgmemalloc"}, $ans{"sar-lgmemfail"}, $ans{"sar-ovszalloc"}, $ans{"sar-ovszallocfail"}, $ans{"sar-fiveminload"}, $ans{"sar-fifteenminload"}) = split(/\s+/, $lines[2]);
			&debug("ParseSar found solaris collect_stats.pl output. 5 min load: " . $ans{"sar-fiveminload"});
		} else {
			&debug("ParseSar couldnt parse collect_stats.pl output: $lines[1]");
		}

	} else {
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse sar output."; &Log($SSHPERFmessage);}
	}
}

sub ParseSnmp() {
        my ($test, $res) = @_;

	&debug("ParseSnmp: parsing: $res");


	if ($test eq "snmp-winprocessorload") {
		if ($res =~ /hrProcessorLoad.1\s+(\d+)/) {
			&debug("ParseSnmp: found processor load: $1");
			$ans{$test} = $1;
		}
	} elsif ($test eq "snmp-winsystemnumusers") {
		if ($res =~ /hrSystemNumUsers.0\s+(\d+)/) {
			&debug("ParseSnmp: found num users: $1");
			$ans{$test} = $1;
		}
	} elsif ($test eq "snmp-winsystemprocesses") {
		if ($res =~ /hrSystemProcesses.0\s+(\d+)/) {
			&debug("ParseSnmp: found num procs: $1");
			$ans{$test} = $1;
		}
	} elsif ($test eq "snmp-wintcpcurrestab") {
		if ($res =~ /tcpCurrEstab.0\s+(\d+)/) {
			&debug("ParseSnmp: found tcp established sessions: $1");
			$ans{$test} = $1;
		}
	} elsif ($test eq "snmp-ioscpu5min") {
		if ($res =~ /enterprises.9.2.1.57.0\s+(\d+)/) {
			&debug("ParseSnmp: found 5 min cpu: $1");
			$ans{$test} = $1;
		}
	} elsif ($test eq "snmp-iosmem5minused") {
		if ($res =~ /enterprises.9.9.48.1.1.1.5.1\s+(\d+)/) {
			&debug("ParseSnmp: found mem 5 min used: $1");
			$ans{$test} = $1;
		} else { &debug("ParseSnmp: couldn't parse: $res"); }
	} elsif ($test eq "snmp-iosmem5minfree") {
		if ($res =~ /enterprises.9.9.48.1.1.1.6.1\s+(\d+)/) {
			&debug("ParseSnmp: found mem 5 min free: $1");
			$ans{$test} = $1;
		} else { &debug("ParseSnmp: couldn't parse: $res"); }
	} else {
		die("Unknown snmp test");
	}

}

sub ParseSnmpOid() {
        my ($test, $res, $name) = @_;

	&debug("ParseSnmp: parsing: $res");

	if ($test =~ /snmp-oid-(\S+)/) {
		my $testname = $1;
		if ($res =~ /(.*)\s+(\d+)/) {
			&debug("ParseSnmp: found $testname: $2");
			$ans{$test} = $2;
		}
	} else {
		die("snmp-oid failure: $test");
	}

}

sub ParseInterface() {
        my ($int, $line) = @_;

	&debug("ParseInterface: parsing: $line");

# Uptime: 247894  Threads: 29  Questions: 1238341  Slow queries: 3  Opens: 46  Flush tables: 1  Open tables: 39  Queries per second avg: 4.995
	my @values = split(/\s+/, $line);
	($theint, $tmp) = split(":", $values[1]);
	$ans{"int-" . $theint . "-rxbytes"} = $tmp;
	$ans{"int-" . $theint . "-rxpkts"} = $values[2];
	$ans{"int-" . $theint . "-rxerrs"} = $values[3];
	$ans{"int-" . $theint . "-txbytes"} = $values[9];
	$ans{"int-" . $theint . "-txpkts"} = $values[10];
	$ans{"int-" . $theint . "-txerrs"} = $values[11];

	&debug("ParseInterface: found tx/rx bytes (" . $ans{"int-" . $theint . "-txbytes"} . "/" . $ans{"int-" . $theint . "-rxbytes"} . "), pkts (" . $ans{"int-" . $theint . "-txpkts"} . "/" . $ans{"int-" . $theint . "-rxpkts"} . "), errs (" . $ans{"int-" . $theint . "-txerrs"} . "/" . $ans{"int-" . $theint . "-rxerrs"} . ")");

}

sub ParseMysqlStatus() {
        my ($line) = @_;

	&debug("ParseMysqlStat: parsing: $line");

# Uptime: 247894  Threads: 29  Questions: 1238341  Slow queries: 3  Opens: 46  Flush tables: 1  Open tables: 39  Queries per second avg: 4.995
	if ($line =~ /Uptime: (\d+)\s+Threads: (\d+)\s+Questions: (\d+)\s+Slow queries: (\d+)\s+Opens: (\d+)\s+Flush tables: (\d+)\s+Open tables: (\d+)\s+Queries per second avg: (\S+)/) {
		$ans{"mysql-uptime"} = $1;
		$ans{"mysql-threads"} = $2;
		$ans{"mysql-questions"} = $3;
		$ans{"mysql-slowqueries"} = $4;
		$ans{"mysql-opens"} = $5;
		$ans{"mysql-flushtables"} = $6;
		$ans{"mysql-opentables"} = $7;
		$ans{"mysql-queries"} = $8;
		&debug("ParseMysqlStat: found threads, opentables, questions: $2, $7, $3");
	} else { 
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse mysql status."; &Log($SSHPERFmessage);}
		&debug("ParseMysqlStat: unable to parse mysql status");
		$ans{"mysql-uptime"} = -1;
	}
}

sub ParseUptime() {
        my ($line) = @_;
	# &debug("ParseUptime: parsing: $line");
	
	if ($line =~ /load average: \d+\.\d+, (\d+\.\d+), (\d+\.\d+)/) {
		$ans{"load-5minave"} = $1;
		$ans{"load-15minave"} = $2;
		debug("ParseUptime: found 5min load: $1");
	} else { 
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse uptime output."; &Log($SSHPERFmessage);}
	}
}

sub ParseFree() {
        my ($line) = @_;
	@lines = split(/\n/, $line);

	# &debug("ParseFree: parsing");

	if ($lines[2] =~ /^Mem:\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+/) {
		$ans{"mem-total"} = $1;
		$ans{"mem-free"} = $2;
		if ($lines[4] =~ /^Swap:\s+(\d+)\s+\d+\s+(\d+)/) {
			$ans{"swap-total"} = $1;
			$ans{"swap-free"} = $2;
			&debug("ParseFree: found swap: (" . $ans{"swap-free"} . " / " . $ans{"swap-total"} . ")");
			&debug("ParseFree: found free mem: (" . $ans{"mem-free"} . " / " . $ans{"mem-total"} . ")");
		} else { die("ParseFree: parse swap error\n"); }
		$ans{"swap-freepct"} = 100 * ($ans{"swap-free"} / $ans{"swap-total"});
		$ans{"mem-freepct"} = 100 * ($ans{"mem-free"} / $ans{"mem-total"});
	} else { 
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse free output."; &Log($SSHPERFmessage);}
	}
}

sub ParseTop() {
        my ($line) = @_;
	@lines = split(/\n/, $line);

	&debug("ParseTop: parsing: $lines[4]");
	#	Memory: 1024M real, 635M free, 230M swap in use, 922M swap free

#Updated this 5/7/09 MAO to handle top upgrade
#Remove dependency on line position of the Memory string, and allow for new labels:
#Old format:
#     Memory: 16G real, 3798M free, 13G swap in use, 12G swap free
#New format:
#     Memory: 32G phys mem, 28G free mem, 32G total swap, 32G free swap

# comment out the old:
#	if ($lines[4] =~ /^Memory:\s+(\S+)\s+real,\s+(\S+)\s+free,\s+(\S+)\s+swap in use,\s+(\S+)\s+swap free/) {

# add this:
    foreach (@lines) {
        if ( $_  =~ /^Memory:\s+(\S+)\s+(?:\S+\s*)+\,\s+(\S+)\s(?:\S+\s*)+\,\s+(\S+)\s+(?:\S+\s*)+\,\s+(\S+)/) {
            

            $ans{"mem-total"} = $1;
            $ans{"mem-free"} = $2;
            my $swapused = $3;
            
            # Fix 6/17/04 BAW
            # Need to match GB also
            $ans{"swap-free"} = $4;

            # This is for 100% free swap (diff string)
            #       Memory: 1024M real, 635M free, 922M swap free
        # Comment out block below - MAO -     THIS IS DEFUNCT
            #} elsif ($lines[4] =~ /^Memory:\s+(\S+)\s+real,\s+(\S+)\s+free,\s+(\S+)\s+swap free/) {
            #        $ans{"mem-total"} = $1;
            #        $ans{"mem-free"} = $2;
            #        my $swapused = 0;
            #        $ans{"swap-free"} = $3;
            $parsed_top = 1 ;
        } 
#else { 
	}

    unless (defined($parsed_top)) {
        if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse top output."; &Log($SSHPERFmessage);}
        return;
    }
        #}
	

	if ( $ans{"mem-total"} =~ m/G$/ ) {
		$ans{"mem-total"} =~ s/G$//;
		$ans{"mem-total"} *= 1024;
	} else {
		$ans{"mem-total"} =~ s/M$//;
	}
	
	if ( $ans{"mem-free"} =~ m/G$/ ) {
		$ans{"mem-free"} =~ s/G$//;
		$ans{"mem-free"} *= 1024;
	} else {
		$ans{"mem-free"} =~ s/M$//;
	}
	
	if ( $swapused =~ m/G$/ ) {
		$swapused =~ s/G$//;
		$swapused *= 1024;
	} else {
		$swapused =~ s/M$//;
	}
	

	if ( $ans{"swap-free"} =~ m/G$/ ) {
		$ans{"swap-free"} =~ s/G$//;
		$ans{"swap-free"} *= 1024;
	} else {
		$ans{"swap-free"} =~ s/M$//;
	}

	$ans{"swap-total"} = $swapused + $ans{"swap-free"};

	$ans{"swap-total"} = $ans{"swap-total"} * 1024; 
	$ans{"mem-total"} = $ans{"mem-total"} * 1024; 
	$ans{"mem-free"} = $ans{"mem-free"} * 1024; 
	$ans{"swap-free"} = $ans{"swap-free"} * 1024; 

	$ans{"swap-freepct"} = 100 * ($ans{"swap-free"} / $ans{"swap-total"});
	$ans{"mem-freepct"} = 100 * ($ans{"mem-free"} / $ans{"mem-total"});

	&debug("ParseFree: found swap: (" . $ans{"swap-free"} . " / " . $ans{"swap-total"} . ")");
	&debug("ParseFree: found free mem: (" . $ans{"mem-free"} . " / " . $ans{"mem-total"} . ")");
}

sub ParseDf() {
        my ($line) = @_;
	@lines = split(/\n/, $line);

	&debug("ParseDf: parsing");

	foreach $l (@lines) {
		next if ($l =~ /^Filesystem/); 
		next if ($l eq ""); 
		if ($l =~ /^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)$/) {
			$ans{"disk-total-" . $6} = $2;
			$ans{"disk-used-" . $6} = $3;
			$ans{"disk-free-" . $6} = $4;
			$ans{"disk-usedpct-" . $6} = $5;
			&debug("ParseDf: found fs: $6 ($5)"); 
		} else { 
			#if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Couldn't parse df output."; &Log($SSHPERFmessage);}
			next;
		}
	}
}


sub ParseLocalSmtp() {
        my ($line, $host) = @_;
	
	&debug("ParseLocalSmtp: parsing: " . $line);

	if ($line =~ /SMTP OK - (\d+) second response time/) {
		$ans{"local-check_smtp-" . $host} = $1;
		&debug("ParseLocalSmtp: OK: " . $1 . " second response time");
	} elsif ($line =~ /Invalid SMTP response received from host/) {
		$ans{"local-check_smtp-" . $host} = -1;
		&debug("ParseLocalSmtp: CRITICAL: invalid SMTP response");
		if ($SSHPERFstatus < 1) { $SSHPERFstatus = 1; $SSHPERFmessage = "Invalid SMTP response"; &Log($SSHPERFmessage);}
	} elsif ($line =~ /Connection refused by host/) {
		$ans{"local-check_smtp-" . $host} = -2;
		&debug("ParseLocalSmtp: CRITICAL: connection refused by host");
		if ($SSHPERFstatus < 2) { $SSHPERFstatus = 2; $SSHPERFmessage = "Connection refused by host"; &Log($SSHPERFmessage);}
	} else {
		$ans{"local-check_smtp-" . $host} = -3;
		&debug("ParseLocalSmtp: CRITICAL: unknown error");
		if ($SSHPERFstatus < 2) { $SSHPERFstatus = 2; $SSHPERFmessage = "Unknown error"; &Log($SSHPERFmessage);}
	}
}


sub ReadConfig {
	&debug("ReadConfig: Reading config from file: $CFGFILE");
	if (!open(CFILE, $CFGFILE)) { &debug("Fatal: Couldn't open config file: $CFGFILE"); exit(1); }
	my $l=0;
	while (<CFILE>) {
		$l++;
		next if (/^#/);
		next if (/^$/);
		my ($val, @args) = split;
		if (0) {
		} elsif ($val eq "proc-exists") {
			$tests{$val . "-" . $args[1]} = $args[0] . "~" . $args[1];
		} elsif ($val eq "load-5minave") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "cpu-idlepct") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "mem-free") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "swap-free") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "mem-freepct") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "swap-freepct") {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "disk-usedpct") {
			$tests{$val . "-" . $args[2]} = $args[0] . "~" . $args[1];
		} elsif ($val =~ /^sar-/) {
			$tests{$val} = $args[0] . "~" . $args[1];
		} elsif ($val eq "snmp-oid") {
			$tests{$val . "-" . $args[5]} = $args[0] . "~" . $args[1] . "~" . $args[2] . "~" . $args[3] . "~" . $args[4];
		} elsif ($val =~ /^snmp-/) {
			$tests{$val} = $args[0] . "~" . $args[1] . "~" . $args[2] . "~" . $args[3];
		} elsif ($val =~ /^int-/) {
			$tests{$val} = 1;
		} elsif ($val eq "local-check_smtp") {
			$a = shift(@args);
			$b = shift(@args);
			$tests{$val . "-" . $a} = $b;
		} elsif ($val eq "hostname" ) {
			if (!$SNMPHOST ) { $connection{"hostname"} = $args[0]; }
			else { $connection{"hostname"} = $SNMPHOST; }
		} elsif ($val eq "connect") {
			$connection{"host"} = $args[0];
			$connection{"user"} = $args[1];
			$connection{"key"} = $args[2];
		} elsif ($val eq "connectextra") {
			$connection{"extra"} = join(" ", @args);
		} elsif ($val eq "osversion") {
			$connection{"osversion"} = $args[0];
		} elsif ($val eq "debug") {
			$DEBUG=1;
		} elsif ($val eq "mysql-status") {
			$tests{$val} = join("~", @args);
		} else { die("config file error on line $l: unknown statement: $_\n");
		}
# XXX NEW
	}

	close(CFILE);
	&debug("ReadConfig: Done reading config from file: $CFGFILE");
}

sub debug {
	my ($message) = @_;
	printf stderr "debug: " . $message . "\n" if $DEBUG;
}


sub Log {
  my($entry) = @_;

  # if (open(LOGFILE, ">>$LOGFILE")) {

# 	  (@ctime) = localtime(time);
# 	  printf LOGFILE ("%02d/%02d/%02d %02d:%02d\t$entry\n", $ctime[4]+1, $ctime[3], $ctime[5]+1900, $ctime[2], $ctime[1]);
# 	  close LOGFILE;
 #  }
  &debug("Log: $entry\n");

}

sub SubmitPassive {
  my($description, $returncode, $text) = @_;
  my $h;

  open(ECF, ">>$ECFFILE") || die("Couldn't open $ECFFILE: $!\n");

  # $returncode = $SSHPERFstatus;

  if ($returncode == 0) { $ret = "OK"; 
  } elsif ($returncode == 1) { $ret = "WARNING"; 
  } elsif ($returncode == 2) { $ret = "CRITICAL"; 
  } elsif ($returncode == 3) { $ret = "UNKNOWN"; 
  } else { $ret = "UNKNOWN"; } 

 if ($connection{"hostname"}) {
	$h = $connection{"hostname"};
 } else {
	$h = $connection{"host"};
 }

print ECF ("[" . time . "] PROCESS_SERVICE_CHECK_RESULT;" . $h . ";" . $description . ";$returncode;$description $ret - " . $text . "\n");
  &Log("[" . time . "] PROCESS_SERVICE_CHECK_RESULT;" . $h . ";" . $description . ";$returncode;$description $ret - " . $text );

print  ("[" . time . "] PROCESS_SERVICE_CHECK_RESULT;" . $h . ";" . $description . ";$returncode;$description $ret - " . $text . "\n");
  &Log("[" . time . "] PROCESS_SERVICE_CHECK_RESULT;" . $h . ";" . $description . ";$returncode;$description $ret - " . $text );

  close ECF;
}


```
