import mistlib as mist
import numpy as np

# --------------------------------------------------------------------------------
# Jackson-Hunt model for lamellar spacing for eutectic solidification
# Model taken from: 
# Dantzig and Rappaz, Solidification, Chapter 9, EPFL Press, 2017.
# --------------------------------------------------------------------------------
def get_P_JH(g, n_max = 10000):
    # The semianalytic part of of the Jackson-Hunt model is the evaluation of this
    # infinite sum. Emprically, it seems like 10,000 terms is enough for the 
    # result to converge. This sum is the slowest part of the calculation by far.
    # Potentially we could cache P for various values of g if we really need better
    # performance.

    n = np.arange(1, n_max)
    return np.sum(np.sin(n*np.pi*g)*np.sin(n*np.pi*g) / ((n*np.pi)*(n*np.pi)*(n*np.pi)))

def get_AR_JH(gamma_alphal, theta_alpha, m_lalpha, g_alpha, gamma_betal, theta_beta, m_lbeta, g_beta):
    term_alpha = 2.0*gamma_alphal * np.cos(theta_alpha)/(np.abs(m_lalpha) * g_alpha)
    term_beta = 2.0*gamma_betal * np.cos(theta_beta)/(np.abs(m_lbeta) * g_beta)
    AR = np.abs(m_lalpha) * np.abs(m_lbeta) / (np.abs(m_lalpha) + np.abs(m_lbeta) ) * (term_alpha + term_beta)
    return AR

def get_AC_JH(delta_C_0, g_alpha, g_beta, m_lalpha, m_lbeta):
    P_g_alpha = get_P_JH(g_alpha)
    AC = delta_C_0/(g_alpha * g_beta) * np.abs(m_lalpha) * np.abs(m_lbeta) / (np.abs(m_lalpha) + np.abs(m_lbeta) ) * P_g_alpha
    return AC

def get_eutectic_lamellar_spacing(mat, phases):
    # TODO: This needs to check that the material is a binary alloy

    # Get the diffusivity
    solute_diffusivities = mat.phase_properties['liquid'].properties['solute_diffusivities']
    key = list(solute_diffusivities.keys())[0]
    Dl = solute_diffusivities[key].value

    # Get the solubility limits
    c_e_alpha = mat.phase_properties[phases[0]].properties['solubility_limit'].value
    c_e_beta = mat.phase_properties[phases[1]].properties['solubility_limit'].value
    delta_c_e = c_e_beta - c_e_alpha

    # Get the liquidus slopes
    m_lalpha = mat.phase_properties[phases[0]].properties['liquidus_slope'].value
    m_lbeta = mat.phase_properties[phases[1]].properties['liquidus_slope'].value

    # Get the Gibbs-Thomson coefficients
    gamma_alphal = mat.phase_properties[phases[0]].properties['gibbs_thomson_coeff'].value
    gamma_betal = mat.phase_properties[phases[1]].properties['gibbs_thomson_coeff'].value

    # Get the eutectic contact angles
    theta_alpha = mat.phase_properties[phases[0]].properties['eutectic_contact_angle'].value
    theta_beta = mat.phase_properties[phases[1]].properties['eutectic_contact_angle'].value

    theta_alpha = theta_alpha * 2.0*np.pi/360.0
    theta_beta = theta_beta * 2.0*np.pi/360.0

    # Get the solidification velocity
    velocity = mat.solidification_conditions['solidification_velocity'].value

    # Get the average composition
    key = mat.composition['solute_elements'][0]
    c_avg = mat.composition[key].value

    
    g_alpha = (c_avg - c_e_beta)/(c_e_alpha - c_e_beta)
    g_beta = 1.0 - g_alpha  

    # Save the volume fractions to the mist object
    prop_g_alpha = mist.core.Property(name = "phase_volume_fraction", unit = "None", value = g_alpha, print_name = "Phase volume fraction", reference = 'Calcuated in Ramen', print_symbol = "$g$")

    prop_g_beta = mist.core.Property(name = "phase_volume_fraction", unit = "None", value = g_alpha, print_name = "Phase volume fraction", reference = 'Calcuated in Ramen', print_symbol = "$g$")

    mat.solidification_microstructure['phase_fractions'] = {}
    mat.solidification_microstructure['phase_fractions'][phases[0]] = prop_g_alpha
    mat.solidification_microstructure['phase_fractions'][phases[1]] = prop_g_beta


    AC = get_AC_JH(delta_c_e, g_alpha, g_beta, m_lalpha, m_lbeta)
    AR = get_AR_JH(gamma_alphal, theta_alpha, m_lalpha, g_alpha, gamma_betal, theta_beta, m_lbeta, g_beta)

    spacing = np.sqrt(AR * Dl /(AC * velocity))

    # Save the spacing in the mist object
    property = mist.core.Property(name = "eutectic_lamellar_spacing", unit = "m", value = spacing, print_name = "Eutectic lamellar spacing", reference = 'Calcuated in Ramen', print_symbol = "$\\lambda")
    mat.solidification_microstructure['eutectic_lamellar_spacing'] = property

    return spacing

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Orowan model for strengthening due to lamella from eutectic solidification
# Model taken from: 
# Zhou, L., Huynh, T., Park, S. et al. Laser powder bed fusion of Al–10 wt% Ce 
# alloys: microstructure and tensile property. J Mater Sci 55, 14611–14625 (2020). 
# https://doi.org/10.1007/s10853-020-05037-z
#
# Michi, R. A., Sisco, K., Bahl, S. et al. Microstructural evolution and strengthening mechanisms in a heat-treated additively manufactured Al–Cu–Mn–Zr alloy. Mater. Sci. Eng. A, 840, 142928 (2022). 
# https://doi.org/10.1016/j.msea.2022.142928
# --------------------------------------------------------------------------------

def get_orowan_strengthening_lamella(mat, matrix_phase, secondary_phase):
    # First, get the material properties

    # Taylor factor
    M = mat.phase_properties[matrix_phase].properties['taylor_factor'].value

    # Shear modulus of the base element of the matrix
    G = mat.phase_properties[matrix_phase].properties['shear_modulus_base_element'].value

    # Burgers vector
    b = mat.phase_properties[matrix_phase].properties['burgers_vector_base_element'].value

    # Poisson ratio
    poisson_ratio = mat.phase_properties[matrix_phase].properties['poisson_ratio_base_element'].value

    # Eutectic spacing
    eutectic_spacing = mat.solidification_microstructure['eutectic_lamellar_spacing'].value

    # Secondary phase fraction
    g_secondary = mat.solidification_microstructure['phase_fractions'][secondary_phase].value

    # Now calculate the effective radius of the secondary phase
    R = eutectic_spacing / (np.sqrt(3.0 * np.pi / (4.0 * g_secondary) - 1.64))

    # Finally calculate the strengthening
    orowan_strengthening_lamella = M * 0.4 * G * b / (np.pi * np.sqrt(1-poisson_ratio)) * np.log(2.0*R/b) / eutectic_spacing

    return orowan_strengthening_lamella

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Solid solution strengthening
# Model taken from: 
# Michi, R. A., Sisco, K., Bahl, S. et al. Microstructural evolution and strengthening 
# mechanisms in a heat-treated additively manufactured Al–Cu–Mn–Zr alloy. Mater. Sci. Eng. A, 840, 142928 (2022). 
# https://doi.org/10.1016/j.msea.2022.142928
# --------------------------------------------------------------------------------
def get_solid_solution_strengthening(mat, matrix_phase):
    # NOTE: For now assume a binary alloy

    # First, get the material properties

    # Taylor factor
    M = mat.phase_properties[matrix_phase].properties['taylor_factor'].value

    # Shear modulus of the base element of the matrix
    G = mat.phase_properties[matrix_phase].properties['shear_modulus_base_element'].value

    # Burgers vector
    b = mat.phase_properties[matrix_phase].properties['burgers_vector_base_element'].value

    # Poisson ratio
    poisson_ratio = mat.phase_properties[matrix_phase].properties['poisson_ratio_base_element'].value

    # Solute misfit strain
    solute_misfits = mat.phase_properties[matrix_phase].properties['solute_misfit_strains']
    key = list(solute_misfits.keys())[0]
    solute_misfit = solute_misfits[key].value

    # Average matrix composition (I assume this is the same as the solubility limit of the matrix phase)
    c_matrix = mat.phase_properties[matrix_phase].properties['solubility_limit'].value
    c_matrix_fraction = 0.01 * c_matrix

    # Now calculate the solid solution strengthening
    w = 5.0 * b

    ss_strengthening = M * (3./8.)**(2./3.) * ((1.+poisson_ratio)/(1.-poisson_ratio))**(4./3.) \
                        * (w/b)**(1./3.) * G * np.abs(solute_misfit)**(4./3.) * c_matrix_fraction**(2./3.)

    return ss_strengthening
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Grain boundary strengthening via the Hall-Petch effect
# Model taken from: 
# Michi, R. A., Sisco, K., Bahl, S. et al. Microstructural evolution and strengthening 
# mechanisms in a heat-treated additively manufactured Al–Cu–Mn–Zr alloy. Mater. Sci. Eng. A, 840, 142928 (2022). 
# https://doi.org/10.1016/j.msea.2022.142928
# --------------------------------------------------------------------------------
def get_grain_boundary_strengthening(mat):
    # First, get the material properties

    # Hall-Petch coefficient
    k_HP = mat.properties['hall_petch_coefficient'].value

    # Average grain diameter
    d = mat.grain_microstructure['average_grain_diameter'].value

    # Now calculate the grain boundary strengthening
    gb_strengthening = k_HP / np.sqrt(d)

    return gb_strengthening
# --------------------------------------------------------------------------------

