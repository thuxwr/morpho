/*
* MC Beta Decay Spectrum Endpoint Model - Functions
* -----------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 11 January 2016
*
* Purpose:
*
*   Defines constants and functions to be used in endpoint generation and analysis models.
*
*/


functions{


// Set up constants

    real m_electron() {return  510998.910;}			// Electron mass in eV
    real hbar() {return 6.582119514e-16;}               // Reduced Planck's constant in eV*s
    real c() { return  299792458.;}			   	   	 	// Speed of light in m/s
    real omega_c() {return 1.758820088e+11;}		     // Angular gyromagnetic ratio in rad Hz/Tesla
    real freq_c() {return omega_c()/(2. * pi());}			 // Gyromagnetic ratio in Hz/Tesla
    real alpha() { return 7.29735257e-3;}               	   	 // Fine structure constant
    real bohr_radius() { return 5.2917721092e-11;}	 	 	 	// Bohr radius in meters
    real k_boltzmann() {return  8.61733238e-5;}		         	// Boltzmann's constant in eV/Kelvin
    real unit_mass() { return 931.494061e6;}			 	// Unit mass in eV
    real r0_electron() { return square(alpha())*bohr_radius();}  	 	// Electron radius in meters
    //Frequency damping constant (in units of Hz/Tesla^2)
    real seconds_per_year() {return 365.25 * 86400.;}	        	// Seconds in a year

    real kH2() {return 3.0393615525526027e+38;}     //Molecular force constant for H2 from fitting to Dieke (1958) vibrational levels
    real aH2() {return -0.0508447080033;}  //Coefficient of anharmonic term in H2 vibrations from fitting to Dieke (1958)
    real bond_length_H2() {return 7.42e-11;} //In meters

//  Tritium-specific constants

    real tritium_rate_per_eV() {return 2.0e-13;}				 // fraction of rate in last 1 eV
    real tritium_atomic_mass() {return  3.016 * unit_mass();}   	 // Atomic tritium mass in eV
    real tritium_halflife() {return 12.32 * seconds_per_year();}  // Halflife of tritium (in seconds)

// Hydrogen-specific constants

    real hydrogen_atomic_mass() {return  1.00794 * unit_mass();}   	 // Atomic hydrogen mass in eV

// Deuterium specific constants

    real deuterium_atomic_mass() {return  2.01410178 * unit_mass();}   	 // Atomic deuterium mass in eV

// Mass of non-tritium atom in each molecule (eV). Values correspond to (T2, HT, DT, T)

    real[] atomic_masses() {
        real atomic_masses[4];

        atomic_masses[1] <- tritium_atomic_mass();
        atomic_masses[2] <- hydrogen_atomic_mass();
        atomic_masses[3] <- deuterium_atomic_mass();
        atomic_masses[4] <- 0.0;
        return atomic_masses;}

//Finds the reduced mass of a diatomic molecule

    real reduced_mass(real m1, real m2){
        real mu;
        mu <- m1*m2/(m1+m2);
        return mu;
        }

// Create a centered normal distribution function for faster convergence on normal distributions

    real vnormal_lp(real beta_raw, real mu, real sigma) {
        beta_raw ~ normal(0,1);
        return mu + beta_raw * sigma;
        }


// Finds a simplex of isotopolog fractional composition values in the form (f_T2,f_HT,f_DT,fT) given parameters epsilon, kappa, and eta (defined in each model)

    real[] find_composition(real epsilon, real kappa, real eta, int num_iso){
        real composition[num_iso];

        composition[1] <- (2.0*epsilon - 1.0)*eta;
        composition[2] <- (2.0*(1.0-epsilon)*kappa*eta)/(1+kappa);
        composition[3] <- (2.0*(1.0-epsilon)*eta)/(1+kappa);
        composition[4] <- 1.0 - eta;

        return composition;
    }



//Zero-point vibrational energy values calcuating using equations 22-24 in BPR as well as H2 parameters determined by fitting to Dieke (1958) data

    real[] E_zp_values() {
        real mu_values[(size(atomic_masses())-1)];
        real hbar_omega_values[(size(atomic_masses())-1)];
        real E_zp_values[size(atomic_masses())];

        for (i in 1:size(atomic_masses())-1){
            mu_values[i] <- reduced_mass(atomic_masses()[i], tritium_atomic_mass());
            hbar_omega_values[i] <- hbar()*pow((kH2()/mu_values[i]), 0.5);
            E_zp_values[i] <- 0.5*hbar_omega_values[i] - aH2()*pow((0.5*hbar_omega_values[i]), 2);}
        E_zp_values[size(atomic_masses())] <- 0.0;

        return E_zp_values;
        }

//Energy of a given rotation state J for a given isotopolog. mass_s is the mass of the atom other than tritium in the source (mass_s = 0.0 for atomic T)

    real find_E_J(real mass_s, int J){
        real mom_of_inertia;
        real E_J;

        mom_of_inertia <- reduced_mass(mass_s, tritium_atomic_mass())*pow(bond_length_H2(), 2);
        E_J <- J*(J+1)*pow(c(), 2)*pow(hbar(), 2)/(2*mom_of_inertia);

        return E_J;
        }


// Finds translational variance for one isotopolog (Eq. 40 in BPR)
// mass_s is the mass of the atom *other than* tritium in the isotopolog

    real find_sigma_squared_trans_i(real temp, real mass_s, real p_squared) {
        real sigma_squared_trans_i;

        sigma_squared_trans_i <- (p_squared)*(k_boltzmann())*temp/(tritium_atomic_mass() + mass_s);
        return sigma_squared_trans_i;
        }


// Find total translational variance (weighted sum of the isotopolog sigma_squared_trans_i values)
// composition is a simplex that describes the relative concentration of (T2, HT, DT, T)

    real find_total_sigma_squared_trans(real temp, real p_squared, real[] composition){  //composition is a simplex
        real sigma_squared_trans;

        sigma_squared_trans <- 0.0;
        for (i in 1:size(composition)){
            sigma_squared_trans <- sigma_squared_trans + composition[i]*find_sigma_squared_trans_i(temp, atomic_masses()[i], p_squared);
            }

        return sigma_squared_trans;
        }


// Finds variance due to a given rotation state J for a given isotopolog i (Eq. 38 in BPR)

    real find_sigma_squared_J_i(int J, real mass_s, real E_zp, real p_squared){
        real mu;    //Reduced mass of molecule
        real sigma_squared_J_i;

        if (mass_s != 0){
            mu <- reduced_mass(mass_s, tritium_atomic_mass());
            sigma_squared_J_i <- (p_squared/(2.0*tritium_atomic_mass()))*(2.0*mu*E_zp/(3.0*tritium_atomic_mass())+2*pow(c(),2)*pow(hbar(), 2)*J*(J+1)/(3.0*pow(bond_length_H2(),2)*tritium_atomic_mass()));}

        else{
            mu <- tritium_atomic_mass();
            sigma_squared_J_i <- 0.0;}

        return sigma_squared_J_i;
        }

//To be used to find partition function/rotation state probabilities for HT and DT

    real f_heterogenous(int J,  real temp, real mass_s){
        real g_J;
        real f_heterogenous;

        g_J <- 2.0*J+1.0;
        f_heterogenous <- g_J*pow(e(), -find_E_J(mass_s, J)/(k_boltzmann()*temp));
        return f_heterogenous;
        }


// Finds coefficient that gives relative contribution of rotation state to variance for a given J and a given isotopolog i (based on Eq. 16 in BPR and Doss (2007))

    real find_P_J_i(int J, real temp, real mass_s, real lambda){
        real Qo;
        real Qp;
        int jodd;
        int jeven;
        real Z_i;
        real P_J_i;

        Qo <- 0.0;
        Qp <- 0.0;
        jodd <- 1;
        jeven <- 0;

        if (mass_s == tritium_atomic_mass()){
            while (jodd < 10000){
                Qo <- Qo + f_heterogenous(jodd, temp, mass_s);
                jodd <- jodd + 2;}
            while (jeven < 10000){
                Qp <- Qp + f_heterogenous(jeven, temp, mass_s);
                jeven <- jeven + 2;}
            Z_i <- (1.0-lambda)*Qp + lambda*Qo;

            if  (J % 2 == 0 || J == 0){
                P_J_i <- (1.0-lambda)*f_heterogenous(J, temp, mass_s)/Z_i;}
            else{
                P_J_i <- lambda*f_heterogenous(J, temp, mass_s)/Z_i;}
            }

        else if (mass_s == 0.0){
            Z_i  <- 0.0;
            P_J_i <- 0.0;
            }

        else{
            Z_i <- 0.0;
            for (j in 0:10000){
                Z_i <- Z_i + f_heterogenous(j, temp, mass_s);}
                P_J_i <- f_heterogenous(J, temp, mass_s)/Z_i;
            }

        return P_J_i;
        }


// Finds rotational variance for a given isotopolog (summing over all rotation states)

    real find_sigma_squared_rot_i(int num_J, real mass_s, real E_zp, real p_squared, real temp, real lambda){
        real sigma_squared_rot_i;

        sigma_squared_rot_i <- 0;
        for (n in 0:num_J){
            sigma_squared_rot_i <- sigma_squared_rot_i + find_P_J_i(n, temp, mass_s, lambda)*find_sigma_squared_J_i(n, mass_s, E_zp, p_squared);
            }
        return sigma_squared_rot_i;
        }


// Finds total rotational variance (weighted sum of the isotopolog sigma_squared_rot_i values)

    real find_total_sigma_squared_rot(int num_J, real p_squared, real temp, real[] composition, real lambda){ //composition is a simplex
        real sigma_squared_rot;

        sigma_squared_rot <- 0.0;
        for (n in 1:size(composition)){
            sigma_squared_rot <- sigma_squared_rot + composition[n]*find_sigma_squared_rot_i(num_J, atomic_masses()[n], E_zp_values()[n], p_squared, temp, lambda);
            }

        return sigma_squared_rot;
        }


// Finds total average standard deviation sigma_avg, accounting for translational and rotational effects

    real find_sigma(real temp, real p_squared, real[] composition, int num_J, real lambda){       //composition is a simplex
        real sigma_avg;

        sigma_avg <- pow(find_total_sigma_squared_trans(temp, p_squared, composition) + find_total_sigma_squared_rot(num_J, p_squared, temp, composition, lambda), 0.5);

        return sigma_avg;
        }


//Finds uncertainty in translational variance for a given isotopolog due to temperature fluctuations/uncertainty

    real find_delta_sigma_squared_trans_i(real temp, real mass_s, real p_squared, real delta_temp){
        real delta_sigma_squared_trans_i;

        delta_sigma_squared_trans_i <- find_sigma_squared_trans_i(temp, mass_s, p_squared)*delta_temp/temp;

        return delta_sigma_squared_trans_i;
        }



//Finds uncertainty in rotational variance for a given isotopolog due to temperature fluctuations/uncertainty

    real find_delta_sigma_squared_rot_i(real temp, real mass_s, real E_zp, real p_squared, real delta_temp, real lambda){
        real P_0_i;
        real P_1_i;
        real sigma_squared_0_i;
        real sigma_squared_1_i;
        real delta_sigma_squared_rot_i;

        if (mass_s != 0.0){
            P_0_i <- find_P_J_i(0, temp, mass_s, lambda);
            P_1_i <- find_P_J_i(1, temp, mass_s, lambda);
            sigma_squared_0_i <- find_sigma_squared_J_i(0, mass_s, E_zp, p_squared);
            sigma_squared_1_i <- find_sigma_squared_J_i(1, mass_s, E_zp, p_squared);

            delta_sigma_squared_rot_i <- P_0_i*P_1_i*find_E_J(mass_s, 1)/(k_boltzmann()*pow(temp, 2))*(sigma_squared_1_i-sigma_squared_0_i)*delta_temp;
            }

        else{
            delta_sigma_squared_rot_i <- 0.0;
            }

        return delta_sigma_squared_rot_i;
        }


//Finds uncertainty in rotational variance for a given isotopolog due to ortho-para ratio uncertainty

    real find_delta_sigma_squared_OP_i(int num_J, real mass_s, real E_zp, real p_squared, real delta_lambda){
        real sigma_squared_ortho;
        real sigma_squared_para;
        real delta_sigma_squared_OP_i;

        sigma_squared_ortho <- 0.0;
        sigma_squared_para <- 0.0;

        if (mass_s != 0.0){
            for (iter_odd in 0:num_J){
                if (iter_odd == 0 || iter_odd % 2 == 0)
                    sigma_squared_ortho <- sigma_squared_ortho + find_sigma_squared_J_i(iter_odd, mass_s, E_zp, p_squared);
                }
            for (iter_even in 0:num_J){
                if (iter_even != 0 && iter_even % 2 != 0)
                    sigma_squared_para <- sigma_squared_para + find_sigma_squared_J_i(iter_even, mass_s, E_zp, p_squared);
                }

            delta_sigma_squared_OP_i <- (sigma_squared_ortho - sigma_squared_para)*delta_lambda;
            }

        else{
            delta_sigma_squared_OP_i <- 0.0;}

        return delta_sigma_squared_OP_i;
        }


//Finds uncertainty in rotational variance due to uncertainty in epsilon, the fractional activity compared to that of pure T2

    real find_delta_sigma_squared_epsilon(real temp, real p_squared, int num_J, real lambda, real kappa, real eta, real delta_epsilon){
        real sigma_squared_i[3];
        real delta_sigma_squared_epsilon;

        for (p in 1:size(sigma_squared_i)){
            sigma_squared_i[p] <- find_sigma_squared_trans_i(temp, atomic_masses()[p], p_squared) + find_sigma_squared_rot_i(num_J, tritium_atomic_mass(), E_zp_values()[p], p_squared, temp, lambda);}

        delta_sigma_squared_epsilon <- (2.0*sigma_squared_i[1] - 2.0*kappa/(1.9+kappa)*sigma_squared_i[2] - 2.0/(1.0+kappa)*sigma_squared_i[3])*eta*delta_epsilon;

        return delta_sigma_squared_epsilon;
        }


//Finds uncertainty in rotational variance due to uncertainty in kappa, the concentration ratio of HT/DT in the source gas

    real find_delta_sigma_squared_kappa(real temp, real p_squared, int num_J, real lambda, real epsilon, real kappa, real eta, real delta_kappa){
        real sigma_squared_i[3];
        real delta_sigma_squared_kappa;

        for (p in 1:size(sigma_squared_i)){
            sigma_squared_i[p] <- find_sigma_squared_trans_i(temp, atomic_masses()[p], p_squared) + find_sigma_squared_rot_i(num_J, tritium_atomic_mass(), E_zp_values()[p], p_squared, temp, lambda);}

        delta_sigma_squared_kappa <- 2.0*(1.0-epsilon)/pow((1.0+kappa), 2)*(sigma_squared_i[2] - sigma_squared_i[3])*eta*delta_kappa;

        return delta_sigma_squared_kappa;
        }


//Finds uncertainty in rotational variance due to uncertainty in eta (eta=0 --> pure T; eta=1 --> no T present)

    real find_delta_sigma_squared_eta(real temp, real p_squared, int num_J, real lambda, real epsilon, real kappa, real delta_eta){
        real sigma_squared_i[4];
        real delta_sigma_squared_eta;

        for (p in 1:size(sigma_squared_i)){
        sigma_squared_i[p] <- find_sigma_squared_trans_i(temp, atomic_masses()[p], p_squared) + find_sigma_squared_rot_i(num_J, tritium_atomic_mass(), E_zp_values()[p], p_squared, temp, lambda);}

        delta_sigma_squared_eta <- ((2.0*epsilon-1.0)*sigma_squared_i[1] + (2.0*(1.0-epsilon)*kappa)/(1.0+kappa)*sigma_squared_i[2] + (2.0*(1.0-epsilon))/(1.0+kappa)*sigma_squared_i[3] - sigma_squared_i[4])*delta_eta;

    return delta_sigma_squared_eta;
}



//Finds total standard deviation of variance (weighted sum based on isotopolog concentrations)

    real find_delta_sigma(real temp, real p_squared, real delta_temp, int num_J, real delta_lambda, real[] composition, real lambda, real epsilon, real kappa, real eta, real delta_epsilon, real delta_kappa, real delta_eta){
        real delta_sigma_squared;
        real delta_sigma;

        delta_sigma_squared <- find_delta_sigma_squared_epsilon(temp, p_squared, num_J, lambda, kappa, eta, delta_epsilon) + find_delta_sigma_squared_kappa(temp, p_squared, num_J, lambda, epsilon, kappa, eta, delta_kappa) + find_delta_sigma_squared_eta(temp, p_squared, num_J, lambda, epsilon, kappa, delta_eta);

        for (m in 1:size(composition)){
            delta_sigma_squared <- delta_sigma_squared + composition[m]*(find_delta_sigma_squared_trans_i(temp, atomic_masses()[m], p_squared, delta_temp) + find_delta_sigma_squared_rot_i(temp, atomic_masses()[m], E_zp_values()[m], p_squared, delta_temp, lambda) + find_delta_sigma_squared_OP_i(num_J, atomic_masses()[m], E_zp_values()[m], p_squared, delta_lambda));
            }
        delta_sigma <- pow(delta_sigma_squared, 0.5);

        return delta_sigma;
        }

}