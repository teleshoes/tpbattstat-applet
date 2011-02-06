#!/usr/bin/perl
########################################################################
#SVG merging tool v0.1
#Copyright 2011 Elliot Wolk
#
#Very simple tool for placing objects from one SVG file into another.
#
########################################################################
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

use strict;
use warnings;

my $symFile = shift;
my $baseFile = shift;
my $destFile = shift;

open FH, "< $symFile" or die "could not read $symFile\n";
my $sym = join '', <FH>;
close FH;
open FH, "< $baseFile" or die "could not read $baseFile\n";
my $base = join '', <FH>;
close FH;


my $xmlAttRegex = qr/(?:
  \s*
  [a-zA-Z0-9_\-:]+
  \s* = \s*
  (?:
    "
      (?: [^"\\]* | \\" )*
    "
    |
    \'
      (?: [^'\\]* | \\' )*
    \'
  )
  \s*
)/sx;

if($base !~ /
  ^
  (.*)
  (< \s* svg $xmlAttRegex* >)
  (.*)
  (< \s* \/ \s* svg \s* >)
  (.*)
  $
  /sx){
  die "$baseFile is (probably?) malformed";
}

my $baseSvgContent = $3;

if($sym !~ /
  ^
  (.*)
  (< \s* svg $xmlAttRegex* >)
  (.*)
  (< \s* \/ \s* svg \s* >)
  (.*)
  $
  /sx){
  die "$symFile is (probably?) malformed";
}


my $dest = "$1$2$3$baseSvgContent$4$5";

open FH, "> $destFile" or die "could not write $destFile\n";
print FH $dest;
close FH;
