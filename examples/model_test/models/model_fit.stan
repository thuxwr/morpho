/*


*/

functions{}

data {
	int<lower=0> N;
	vector[N] x;
	vector[N] y;
}

parameters{
	real slope;
	real intercept;
	real<lower=0> sigma;

}

model {
	/* Prior. */
	slope ~ normal(0, 1);
	intercept ~ normal(10, 10);
	sigma ~ normal(0,5);

	/* Data distribution. */
	if(N!=0)
		y ~ normal(slope * x + intercept, sigma);
}


