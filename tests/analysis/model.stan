data {
	real rho12;
	real rho13;
	real rho23;
}

parameters {
	real x;
	real y;
	real z;
}

model {
	matrix[3,3] Sigma;
	vector[3] pars;
	vector[3] mu;

	Sigma[1,1] = 1;
	Sigma[2,2] = 1;
	Sigma[3,3] = 1;
	Sigma[1,2] = rho12;
	Sigma[2,1] = rho12;
	Sigma[1,3] = rho13;
	Sigma[3,1] = rho13;
	Sigma[2,3] = rho23;
	Sigma[3,2] = rho23;
	mu[1] = 0;
	mu[2] = 0;
	mu[3] = 0;
	pars[1] = x;
	pars[2] = y;
	pars[3] = z;
	pars ~ multi_normal(mu, Sigma);
}
