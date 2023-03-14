public class WeakNightVoter implements AccessDecisionVoter {
    @Override
    public int vote(Authentication authentication, Object object, Collection collection) {  // Noncompliant
      Calendar calendar = Calendar.getInstance();
      int currentHour = calendar.get(Calendar.HOUR_OF_DAY);
      return ACCESS_ABSTAIN; // Noncompliant
    }
}