#!/usr/bin/perl
use strict;
use warnings;

my @heights = (18, 20, 24, 36, 40, 48, 64);

sub run(@){
  print "@_\n";
  system @_;
}

sub convertRsvg($$$){
  my ($src, $dest, $h) = @_;
  run "rsvg",
    "-h", $h,
    "-a",
    "-f", "png",
    "-o", $dest,
    $src, "$dest";
}
sub convertImageMagick($$$){
  my ($src, $dest, $h) = @_;
  run "convert", "-resize", "${h}", $src, $dest;
}

sub convert($$$){
  my $baseName = shift;
  my $baseDir = shift;
}

sub main(@){
  chdir 'icons';
  my @imgs = `cd svg; find -name '*.svg'`;

  run "rm", "-r", "xpm";
  run "rm", "-r", "png";

  for my $h(@heights){
    for my $img(@imgs){
      chomp $img;

      my $baseName = $img;
      $baseName =~ s/\.([a-zA-Z0-9]+)$//;

      my $baseDir = $baseName;
      $baseDir =~ s/\/[^\/]*$//;

      my $size = "${h}x${h}";

      run "mkdir", "-p", "png/$size/$baseDir";
      convertRsvg "svg/$baseName.svg", "png/$size/$baseName.png", $h;
      
      run "mkdir", "-p", "xpm/$size/$baseDir";
      convertImageMagick "svg/$baseName.svg", "xpm/$size/$baseName.xpm", $h;
    }
  }
}

&main(@ARGV);
