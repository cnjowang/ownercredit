
from misc import *
import filtered


# Test the base averaged class.  Acts like a plain integer or float value, but is charged with
# timestamped values using the .sample( value [, time ] ) method.  Implements a simple average of
# all sample values within the time span specified at creation.
def test_averaged():
    a			= filtered.averaged( 10., 0., 90. )
    assert near( 0.0000, a )
    assert near( 0.5000, a.sample(  1.,  91. ))
    assert near( 1.0000, a.sample(  2.,  94. ))
    assert near( 2.0000, a.sample(  3., 100. ))

    a			= filtered.averaged( 10., 5., 1. )
    assert near( 5.0, a )
    assert near( 4.5, a.sample(  4.,  2. ))
    assert near( 4.5, a )
    assert near( 5.0, a.sample(  6.,  3. ))
    assert near( 5.0, a )
    assert near( 5.0, a.sample(  5.,  4. ))
    assert near( 5.0, a.sample(  5., 10. ))
    assert 5 == len( a.history )
    assert near( 5.25,a.sample(  5., 12. ))	# timestamps 3-12 now within interval 10; 1-2 drop off
    assert 4 == len( a.history )
    assert near( 5.0, a.sample(  5., 13. )) 	# 0 x 4, 4 x 5, 1 x 6
    assert near( 5.0, a.sample(  5., 14. ))
    assert near( 5.0, a )


# Test the (better) weighted_linear classs
def test_weighted_linear():
    w			= filtered.weighted_linear( 10., 0., 90. )
    assert near( 0.0000, w )
    assert near( 0.0000, w.sample(  1.,  91. ))	# 0. has interval of 1. (90. to 91.); 1.0 has no interval yet
    assert len( w.history ) == 2
    assert near( 0.7500, w.sample(  2.,  94. ))	# 0. has interval of 1., 1. has interval of 3. (91. to 94.)
    assert len( w.history ) == 3
    assert near( 1.5000, w.sample(  3., 100. ))	# 0. x 1., 1. x 3., 2. x 6.

    w			= filtered.weighted_linear( 10., 5., 1. )
    assert near( 5.0, w )			# Single value so far
    assert near( 5.0, w.sample(  4.,  2. ))	# The 5. has now been in effect for 1. of the interval; 4. has no interval yet
    assert near( 5.0, w )
    assert near( 4.5, w.sample(  6.,  3. ))	# Now 5. and 4. have been in effect for 1. (each); 6. has no interval yet
    assert near( 4.5, w )
    assert near( 5.0, w.sample(  5.,  4. ))	# 4. and 6. now each in effect for 1.; 5. not yet
    assert near( 5.0, w.sample(  5., 10. ))
    assert near( 5.0, w.sample(  5., 12. ))	# Drops the 4. (but retains for time-weighted average!)
    assert near( 5.1, w.sample(  5., 13. ))	# Drops the 6. (but ...)
    assert near( 5.0, w.sample(  5., 14. ))	# Finally, only 5.'s in effect
    assert near( 5.0, w )

# We can simulate linear by putting ending values at the same 
# timestamp as the next beginning value.  Uses same tests as
# test_weighted_linear above
def test_weighted_with_simultaneous():
    w			= filtered.weighted( 10., 0., 90. )
    assert near( 0.0000, w )
    assert near( 0.0000, w.sample(  0.,  91. ))
    assert near( 0.0000, w.sample(  1.,  91. ))	# 0. has interval of 1. (90. to 91.); 1.0 has no interval yet
    assert len( w.history ) == 3
    assert near( 0.7500, w.sample(  1.,  94. ))
    assert near( 0.7500, w.sample(  2.,  94. ))	# 0. has interval of 1., 1. has interval of 3. (91. to 94.)
    assert len( w.history ) == 5
    assert near( 1.5000, w.sample(  2., 100. ))
    assert near( 1.5000, w.sample(  3., 100. ))	# 0. x 1., 1. x 3., 2. x 6.

    w			= filtered.weighted( 10., 5., 1. )
    assert near( 5.0, w )			# Single value so far
    assert near( 5.0, w.sample(  5.,  2. ))
    assert near( 5.0, w.sample(  4.,  2. ))	# The 5. has now been in effect for 1. of the interval; 4. has no interval yet
    assert near( 5.0, w )
    assert near( 4.5, w.sample(  4.,  3. ))
    assert near( 4.5, w.sample(  6.,  3. ))	# Now 5. and 4. have been in effect for 1. (each); 6. has no interval yet
    assert near( 4.5, w )
    assert near( 5.0, w.sample(  6.,  4. ))
    assert near( 5.0, w.sample(  5.,  4. ))	# 4. and 6. now each in effect for 1.; 5. not yet
    assert near( 5.0, w.sample(  5., 10. ))
    assert near( 5.0, w.sample(  5., 12. ))	# Drops the 4. (but retains for time-weighted average!)
    assert near( 5.1, w.sample(  5., 13. ))	# Drops the 6. (but ...)
    assert near( 5.0, w.sample(  5., 14. ))	# Finally, only 5.'s in effect
    assert near( 5.0, w )

# Test the (best) weighted class.  Uses a weighted average of each sample, weighted by their
# duration vs. the total interval of the filter.  Until the initially specified time span is full of
# values, the average only reflects the shorter (actual) time span of the values specified thus far.
def test_weighted():
    w			= filtered.weighted( 10., 0., 90. )
    assert near( 0.0000, w )
    assert len( w.history ) == 1
    assert near( w.interval, 10. )
    assert near( 0.5000, w.sample(  1.,  91. ))	# 0.-->1.(.5) has interval of 1. (90. to 91.); 1.0 has no interval yet
    assert len( w.history ) == 2
    assert near( 1.2500, w.sample(  2.,  94. ))	# 0.5 has interval of 1., 1.-->2.(1.5) has interval of 3. (91. to 94.) 5/4==1.25
    assert len( w.history ) == 3
    assert near( 2.0000, w.sample(  3., 100. ))	# .5 x 1., 1.5 x 3., 2.5 x 6. == .5+4.5+15/10 == 2.0

    w			= filtered.weighted( 10., 5., 1. )
    assert near( 5.00, w )			# Single value so far
    assert near( 4.50, w.sample(  4.,  2. ))	# The 5.-->4. has now been in effect for 1. of the interval
    assert near( 4.50, w )
    assert near( 4.75, w.sample(  6.,  3. ))	# Now 5. and 4. have been in effect for 1. (each); followed by 6
    assert near( 4.75, w )
    assert near( 5.00, w.sample(  5.,  4. ))	# 4. and 6. now each in effect for 1.; now another 5.
    assert near( 5.00, w.sample(  5., 10. ))
    assert near( 5.05, w.sample(  5., 12. ))	# Drops the 4. (but retains for time-weighted average!)
    assert near( 5.05, w.sample(  5., 13. ))	# Drops the 6. (but ...)
    assert near( 5.00, w.sample(  5., 14. ))	# Finally, only 5.'s in effect
    assert near( 5.00, w )


# 
# WARNING
# 
#     filtered.filter is obsolete; use filtered.averaged et. al. instead.
# 

# A simple summing filter over 10. time units, starting at time 0.
def test_filter():
    f			= filtered.filter( 10., 0. )
    assert near( 0.0000, f.add(  0.,  90. ))
    assert near( 0.5000, f.add(  1.,  91. ))
    assert near( 1.0000, f.add(  2.,  94. ))
    assert near( 2.0000, f.add(  3., 100. ))

    f			= filtered.filter( 10., 0. )
    assert near( 5.0, f.add(  5.,  1. ))
    assert near( 4.5, f.add(  4.,  2. ))
    assert near( 4.5, f.get(),         )
    assert near( 5.0, f.add(  6.,  3. ))
    assert near( 5.0, f.get()          )
    assert near( 5.0, f.add(  5.,  4. ))
    assert near( 5.0, f.add(  5., 10. ))
    assert 5 == len( f.history )
    assert near( 5.25,f.add(  5., 12. ))	# timestamps 3-12 now within interval 10; 1-2 drop off
    assert 4 == len( f.history )
    assert near( 5.0, f.add(  5., 13. )) 	# 0 x 4, 4 x 5, 1 x 6
    assert near( 5.0, f.add(  5., 14. ))
    assert near( 5.0, f.get()         )

# A time-weighted filter over 10. time units, starting at time 0., and initial value 0.
def test_filter_weighted():
    f			= filtered.filter( ( 10., 0. ), 0. )
    assert near( 0.0000, f.add(  0.,  90. ))
    assert near( 0.0000, f.add(  1.,  91. ))
    assert near( 0.3000, f.add(  2.,  94. ))
    assert near( 1.5000, f.add(  3., 100. ))

    f			= filtered.filter( ( 10., 0. ), 0. )
    assert near( 0.0, f.add(  5.,  1. ))	# No effect 'til later; time-weighted samples have 0. time weight when first entered!
    assert near( 0.5, f.add(  4.,  2. ))	# The 5. has now been in effect for 1. of the interval 10.
    assert near( 0.5, f.get(),         )
    assert near( 0.9, f.add(  6.,  3. ))	# Now 5. and 4. have been in effect for 1. (each) of 10.
    assert near( 0.9, f.get(),         )
    assert near( 1.5, f.add(  5.,  4. ))
    assert near( 0.0, f.weighted );
    assert near( 4.5, f.add(  5., 10. ))
    assert near( 0.0, f.weighted );
    assert near( 5.0, f.add(  5., 12. ))	# Drops the 4. (but retains for time-weighted average!)
    assert near( 4.0, f.weighted );
    assert near( 5.1, f.add(  5., 13. ))	# Drops the 6. (but ...)
    assert near( 5.0, f.add(  5., 14. ))	# Finally, only 5.'s in effect
    assert near( 5.0, f.get(),         )

def test_filter_weighted_interval():
    f			= filtered.filter( ( 10., 0. ), 0. )
    assert near( 0.0, f.add(  5.,  1. ))	# No effect 'til later; time-weighted samples have 0. time weight when first entered!
    assert near( 0.5, f.add(  4.,  2. ))	# The 5. has now been in effect for 1. of the interval 10.
    assert near( 0.9, f.add(  6.,  3. ))	# Now 5. and .4 have been in effect for 1. (each) of 10.
    assert len( f.history ) == 3
    # now, set the interval to 0, and test effects
    f.interval		= 0.
    assert near( 6.0,  f.get() )		# Should now be instantaneous value
    assert len( f.history ) == 3
    assert near( 7.0,  f.add( 7., 4. ))
    assert len( f.history ) == 1
    assert near( 7.0,  f.get() )
    assert near( 8.0,  f.add( 8., 5. ))
    assert near( 8.0,  f.get() )