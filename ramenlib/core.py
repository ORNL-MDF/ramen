import mistlib as mist
import numpy as np

def get_P_JH(g, n_max = 10000):
    sum = 0.0
    for n in range(1,n_max):
        sum = sum + np.sin(n*np.pi*g)**2 / ( (n*np.pi)**3 )
    return sum    

def get_AR_JH(gamma_alphal, theta_alpha, m_lalpha, g_alpha, gamma_betal, theta_beta, m_lbeta, g_beta):
    term_alpha = 2.0*gamma_alphal * np.cos(theta_alpha)/(np.abs(m_lalpha) * g_alpha)
    term_beta = 2.0*gamma_betal * np.cos(theta_beta)/(np.abs(m_lbeta) * g_beta)
    AR = np.abs(m_lalpha) * np.abs(m_lbeta) / (np.abs(m_lalpha) + np.abs(m_lbeta) ) * (term_alpha + term_beta)
    return AR

def get_AC_JH(delta_C_0, g_alpha, g_beta, m_lalpha, m_lbeta):
    P_g_alpha = get_P_JH(g_alpha)
    AC = delta_C_0/(g_alpha * g_beta) * np.abs(m_lalpha) * np.abs(m_lbeta) / (np.abs(m_lalpha) + np.abs(m_lbeta) ) * P_g_alpha
    return AC

def get_eutectic_lamellar_spacing(mat, velocity, c_avg, phases):
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

    
    g_alpha = (c_avg - c_e_beta)/(c_e_alpha - c_e_beta)
    g_beta = 1.0 - g_alpha  

    AC = get_AC_JH(delta_c_e, g_alpha, g_beta, m_lalpha, m_lbeta)
    AR = get_AR_JH(gamma_alphal, theta_alpha, m_lalpha, g_alpha, gamma_betal, theta_beta, m_lbeta, g_beta)

    spacing = np.sqrt(AR * Dl /(AC * velocity))
    return spacing